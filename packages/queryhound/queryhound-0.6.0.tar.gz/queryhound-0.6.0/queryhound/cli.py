import argparse
import json
from datetime import datetime
from statistics import mean, median, quantiles
from collections import defaultdict
from tabulate import tabulate
import csv
import sys
import re
import os
from pathlib import Path
from . import __version__

TRUNC_PLAN_LEN = 60
TRUNC_APP_LEN = 40
TRUNC_SHAPE_LEN = 80
TRUNC_ERRMSG_LEN = 120


def _truncate(text, max_len, verbose=False):
    if verbose:
        return text
    if text is None:
        return ''
    s = str(text)
    if len(s) <= max_len:
        return s
    return s[: max_len - 1] + '…'


def _ensure_user_path_updated():
    """Attempt to ensure the user install bin directory is on PATH.

    This is a best-effort, non-interactive helper. It prepends the bin path for the
    running interpreter's user base (e.g. ~/Library/Python/3.13/bin on macOS) to PATH for
    the current process and, if not already present in the user's shell startup file,
    appends a line to ~/.zprofile (preferred for login shells) or ~/.zshrc as fallback.

    Opt-out: set environment variable QUERYHOUND_SKIP_PATH_UPDATE=1 before running.
    """
    if os.environ.get("QUERYHOUND_SKIP_PATH_UPDATE") == "1":
        return
    try:
        user_base = sys.base_prefix  # fallback; better via site.getusersitepackages()
        try:
            import site
            user_base = site.getuserbase()
        except Exception:
            pass
        candidate_bin = Path(user_base) / "bin"
        if not candidate_bin.exists():
            # macOS user installs often are in ~/Library/Python/{major.minor}/bin
            alt = Path.home() / "Library" / "Python" / f"{sys.version_info.major}.{sys.version_info.minor}" / "bin"
            if alt.exists():
                candidate_bin = alt
        # Update in-process PATH
        path_parts = os.environ.get("PATH", "").split(":")
        if str(candidate_bin) not in path_parts:
            os.environ["PATH"] = f"{candidate_bin}:{os.environ.get('PATH','')}"
        # Persist for future shells if missing
        zprofile = Path.home() / ".zprofile"
        zshrc = Path.home() / ".zshrc"
        target_rc = zprofile if zprofile.exists() else zshrc
        export_line = f'export PATH="{candidate_bin}:$PATH"'\
            if str(candidate_bin) not in os.environ.get("PATH", "") else None
        if export_line:
            try:
                # Only append if not already present in the file
                if target_rc.exists():
                    existing = target_rc.read_text(errors="ignore")
                    if str(candidate_bin) in existing:
                        return
                with target_rc.open("a") as fh:
                    fh.write(f"\n# Added by queryhound to ensure qh is on PATH\n{export_line}\n")
            except Exception:
                pass
    except Exception:
        pass


def parse_date(date_str):
    formats = [
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d"
    ]
    for fmt in formats:
        try:
            if fmt.endswith("%z") and "+00:00" not in date_str and "-" not in date_str[-6:]:
                date_str += "+00:00"
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"Invalid date format: {date_str}")


def parse_log_line(line):
    try:
        entry = json.loads(line)
        timestamp = entry.get("t", {}).get("$date")
        if timestamp:
            timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))

        attr = entry.get("attr", {})
        ns = attr.get("ns")
        ms = attr.get("durationMillis") or attr.get("ms")
        query = attr.get("query") or attr.get("filter")
        plan = attr.get("planSummary")
        command = entry.get("msg", "")
        # Command object (raw) for deriving query shape when available
        command_obj = attr.get("command") if isinstance(attr.get("command"), dict) else None
        query_shape_hash = attr.get("queryShapeHash") or attr.get("queryShapeId")
        query_shape = None
        if query_shape_hash:
            query_shape = query_shape_hash
        elif command_obj:
            op_keys_priority = ["find", "aggregate", "update", "delete", "insert", "count"]
            primary = next((k for k in op_keys_priority if k in command_obj), None)
            if not primary and command_obj:
                primary = next(iter(command_obj.keys()))
            extras = []
            if "pipeline" in command_obj and isinstance(command_obj.get("pipeline"), list):
                extras.append(f"pipeline[{len(command_obj['pipeline'])}]")
            if "filter" in command_obj:
                extras.append("filter")
            if "query" in command_obj:
                extras.append("query")
            # Shallow detection of $match stage
            try:
                snippet = json.dumps(command_obj, default=str)[:800]
                if "$match" in snippet:
                    extras.append("$match")
            except Exception:
                pass
            parts = [p for p in [primary] + extras if p]
            if parts:
                query_shape = ":".join(parts)
        # Try multiple locations for application name seen in connection metadata
        app_name = (
            attr.get("appName")
            or attr.get("applicationName")
            or (attr.get("client", {}).get("application", {}).get("name") if isinstance(attr.get("client"), dict) else None)
            or ""
        )
        keys_examined = attr.get("keysExamined", 0)
        docs_examined = attr.get("docsExamined", 0)
        nreturned = attr.get("nreturned", 0)
        remote_ip = attr.get("remote", "")
        if remote_ip:
            remote_ip = remote_ip.split(":")[0]
        app_name_cleaned = re.sub(r" v[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+", "", app_name)
        app_name_cleaned = re.sub(r"\s*\(.*\)", "", app_name_cleaned)

        operation = "Unknown"
        cmd_l = command.lower()
        attr_type = attr.get("type")
        # Detect connection acceptance events
        if "connection accepted" in cmd_l or ("connection" in cmd_l and "accepted" in cmd_l):
            operation = "Connection"
        elif attr_type:  # Prefer explicit attr.type when present
            operation = str(attr_type).capitalize()
        elif 'find' in command.lower():
            operation = "Find"
        elif 'insert' in command.lower():
            operation = "Insert"
        elif 'update' in command.lower():
            operation = "Update"
        elif 'delete' in command.lower():
            operation = "Delete"

        return {
            'timestamp': timestamp,
            'namespace': ns,
            'ms': ms,
            'query': query,
            'plan': plan,
            'command': command,
            'operation': operation,
            'app_name': app_name_cleaned,
            'keys_examined': keys_examined,
            'docs_examined': docs_examined,
            'nreturned': nreturned,
            'line': line.strip(),
            'remote_ip': remote_ip,
            'query_shape': query_shape
        }

    except json.JSONDecodeError:
        return None


def is_within_date(timestamp, start_date, end_date):
    if not timestamp:
        return False
    if start_date and timestamp < start_date:
        return False
    if end_date and timestamp > end_date:
        return False
    return True


def process_log(file_path, args):
    results = defaultdict(lambda: {'ms_list': [], 'count': 0, 'plan': '', 'namespace': '', 'operation': '', 'app_name': '', 'keys_examined': 0, 'docs_examined': 0, 'nreturned': 0, 'remote_ip': '', 'query_shape': ''})
    log_lines = []

    with open(file_path, 'r') as f:
        for line in f:
            if args.filter and not any(m.lower() in line.lower() for m in args.filter):
                continue

            entry = parse_log_line(line)
            if not entry:
                continue

            if not is_within_date(entry['timestamp'], args.start_date, args.end_date):
                continue
            if args.min_ms is not None and (entry['ms'] is None or entry['ms'] < args.min_ms):
                continue
            # Scan mode: include any plan summaries that contain COLLSCAN
            if args.scan and (entry['plan'] is None or "COLLSCAN" not in str(entry['plan'])):
                continue
            if args.slow and (entry['ms'] is None or entry['ms'] < 100):
                continue
            if args.namespace and args.namespace != entry['namespace']:
                continue
            if entry['ms'] is None:
                continue
            # Connection aggregation handled separately

            key = (entry['operation'], entry['plan'], entry['namespace'], str(entry['query']))
            results[key]['ms_list'].append(entry['ms'])
            results[key]['count'] += 1
            results[key]['plan'] = entry['plan']
            results[key]['namespace'] = entry['namespace']
            results[key]['operation'] = entry['operation']
            results[key]['app_name'] = entry['app_name']
            results[key]['keys_examined'] += entry['keys_examined']
            results[key]['docs_examined'] += entry['docs_examined']
            results[key]['nreturned'] += entry['nreturned']
            results[key]['remote_ip'] = entry['remote_ip']
            if entry.get('query_shape') and not results[key]['query_shape']:
                results[key]['query_shape'] = entry['query_shape']

            if args.filter:
                log_lines.append(entry['line'])

    return results, log_lines


def process_connections(file_path, args):
    """Aggregate connection-accepted events by remote IP and app name."""
    from collections import Counter
    counts = Counter()
    with open(file_path, 'r') as f:
        for line in f:
            if args.filter and not any(m.lower() in line.lower() for m in args.filter):
                continue
            entry = parse_log_line(line)
            if not entry:
                continue
            # Date filtering if present
            if not is_within_date(entry['timestamp'], args.start_date, args.end_date):
                continue
            if entry.get('operation') != 'Connection':
                continue
            ip = entry.get('remote_ip') or 'Unknown'
            app = entry.get('app_name') or ''
            counts[(ip, app)] += 1
    # Prepare rows sorted by count desc
    rows = [ (ip, app, cnt) for (ip, app), cnt in counts.most_common() ]
    return rows


def summarize_results(results, pvalue=None, include_pstats=False, verbose=False, truncate=False):
    table = []

    for (operation, plan, namespace, query), data in results.items():
        ms_list = data['ms_list']
        count = data['count']
        if not ms_list:
            continue
        # Truncate fields for non-verbose display
        if truncate:
            display_plan = _truncate(plan, TRUNC_PLAN_LEN, verbose=verbose)
            display_app = _truncate(data['app_name'], TRUNC_APP_LEN, verbose=verbose)
            display_shape = _truncate(data.get('query_shape') or '', TRUNC_SHAPE_LEN, verbose=verbose)
        else:
            display_plan = plan
            display_app = data['app_name']
            display_shape = data.get('query_shape') or ''

        row = [operation, display_plan, display_shape]
        if pvalue and pvalue.lower() == 'p50':
            row.append(round(median(ms_list), 2))

        avg_ms = round(mean(ms_list), 2)
        row.append(avg_ms)
        row.extend([
            data['keys_examined'],
            data['docs_examined'],
            data['nreturned']
        ])

        if include_pstats or (pvalue and pvalue.lower() in ['p75', 'p90', 'p99']):
            try:
                q = quantiles(ms_list, n=100)
            except:
                q = []

            if include_pstats or (pvalue and pvalue.lower() == 'p75'):
                row.append(q[74] if len(q) > 74 else '-')
            if include_pstats or (pvalue and pvalue.lower() == 'p90'):
                row.append(q[89] if len(q) > 89 else '-')
            if include_pstats or (pvalue and pvalue.lower() == 'p99'):
                row.append(q[98] if len(q) > 98 else '-')

        row.extend([
            data['operation'],
            count,
            display_app
        ])
        table.append(row)

    return table


def write_csv(output_file, data, headers):
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        writer.writerows(data)


def main():
    # Ensure PATH includes user scripts dir so invoking `qh` after install works without manual edits.
    _ensure_user_path_updated()
    parser = argparse.ArgumentParser(description="QueryHound - MongoDB Log Filter Tool")
    parser.add_argument("logfile", nargs='?', help="Path to MongoDB JSON log file")
    parser.add_argument("--scan", action="store_true", help="Only show COLLSCAN queries")
    parser.add_argument("--slow", action="store_true", help="Only show slow queries (ms >= 100)")
    parser.add_argument("--start-date", type=str, help="Start date (ISO 8601 or 'YYYY-MM-DD')")
    parser.add_argument("--end-date", type=str, help="End date (ISO 8601 or 'YYYY-MM-DD')")
    parser.add_argument("--namespace", type=str, help="Filter by namespace (db.collection)")
    parser.add_argument("--min-ms", type=int, help="Minimum duration (ms)")
    parser.add_argument("--pstats", action="store_true", help="Include P75, P90, P99 stats")
    parser.add_argument("--pvalue", type=str, choices=['P50', 'P75', 'P90', 'P99'], help="Specify a specific p-stat to include")
    parser.add_argument("--output-csv", type=str, help="Write output to CSV")
    parser.add_argument("--filter", nargs='*', type=str, help="Search for lines containing any of the specified strings")
    parser.add_argument("--connections", action="store_true", help="Displays connection counts grouped by IP and app name")
    parser.add_argument("--error", action="store_true", help="Show only error / fatal log lines (severity E/F)")
    parser.add_argument("--verbose", action="store_true", help="Show full field values without truncation")
    parser.add_argument("-v", "--version", action="store_true", help="Show version and exit")

    args = parser.parse_args()

    try:
        if args.version:
            print(f"queryhound version {__version__}")
            sys.exit(0)

        # Connections mode doesn't require other options
        if args.connections:
            if not args.logfile:
                parser.print_help()
                print("\nError: logfile is required for --connections mode.")
                sys.exit(2)
            # parse dates if provided
            results = process_connections(args.logfile, args)
            if results:
                print("\nConnections:")
                # Truncate app name unless verbose
                if not args.verbose:
                    display_rows = []
                    for ip, app, cnt in results:
                        display_rows.append([ip, _truncate(app, TRUNC_APP_LEN, verbose=False), cnt])
                else:
                    display_rows = results
                print(tabulate(display_rows, headers=["Remote IP", "App Name", "Count"], tablefmt="pretty"))
            else:
                print("No connections found in the provided timeframe.")
            sys.exit(0)

        # Error mode
        if args.error:
            if not args.logfile:
                parser.print_help()
                print("\nError: logfile is required for --error mode.")
                sys.exit(2)
            # Process errors
            rows = []
            try:
                with open(args.logfile, 'r') as f:
                    for line in f:
                        try:
                            entry = json.loads(line)
                        except Exception:
                            continue
                        sev = entry.get('s')
                        if sev not in ('E','F'):
                            continue
                        ts_raw = entry.get('t',{}).get('$date')
                        try:
                            ts_disp = datetime.fromisoformat(ts_raw.replace('Z','+00:00')).isoformat() if ts_raw else '-'
                        except Exception:
                            ts_disp = ts_raw or '-'
                        comp = entry.get('c','')
                        _id = entry.get('id','')
                        msg = entry.get('msg','')
                        if not args.verbose:
                            msg = _truncate(msg, TRUNC_ERRMSG_LEN, verbose=False)
                        sev_disp = 'Error' if sev=='E' else 'Fatal'
                        rows.append([ts_disp, sev_disp, comp, _id, msg])
                if rows:
                    print("\nErrors:")
                    print(tabulate(rows, headers=["Timestamp","Severity","Component","ID","Message"], tablefmt="pretty"))
                else:
                    print("No error/fatal entries found.")
            except Exception as e:
                print(f"Error processing error log lines: {e}")
                sys.exit(1)
            sys.exit(0)

        if not args.logfile:
            parser.print_help()
            print("\nError: logfile is required unless --version is used.")
            sys.exit(2)
        args.start_date = parse_date(args.start_date) if args.start_date else None
        args.end_date = parse_date(args.end_date) if args.end_date else None
    except ValueError as e:
        print(f"Date parsing error: {e}")
        sys.exit(1)

    try:
        results, log_lines = process_log(args.logfile, args)

        table = []
        headers = []

        if results and (args.scan or args.slow or args.pstats or args.pvalue):
            table = summarize_results(
                results,
                pvalue=args.pvalue,
                include_pstats=args.pstats,
                verbose=args.verbose,
                truncate=(not args.verbose and (args.slow or args.scan))
            )
            if table:
                headers = ["Operation", "Plan", "Query Shape"]
                if args.pvalue and args.pvalue.lower() == 'p50':
                    headers.append("P50")
                headers += ["Avg ms", "Keys Examined", "Docs Examined", "NReturned"]
                if args.pstats or (args.pvalue and args.pvalue.lower() in ['p75', 'p90', 'p99']):
                    if args.pstats or (args.pvalue and args.pvalue.lower() == 'p75'):
                        headers.append("P75")
                    if args.pstats or (args.pvalue and args.pvalue.lower() == 'p90'):
                        headers.append("P90")
                    if args.pstats or (args.pvalue and args.pvalue.lower() == 'p99'):
                        headers.append("P99")
                headers += ["Operation Type", "Count", "App Name"]

                print("\nSummary Table:")
                print(tabulate(table, headers=headers, tablefmt="pretty"))

        if args.filter and log_lines:
            print("\nMatching Log Lines:")
            for line in log_lines:
                print(line)

        if args.output_csv and table:
            write_csv(args.output_csv, table, headers)

    except Exception as e:
        print(f"Error processing the log file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
    
def run():
    main()