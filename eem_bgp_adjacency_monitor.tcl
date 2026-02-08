::cisco::eem::event_register_syslog pattern "%ROUTING-BGP-5-ADJCHANGE_DETAIL" maxrun_sec 40

namespace import ::cisco::eem::*
namespace import ::cisco::lib::*

# ----------------------------
# PARAMETERS
# ----------------------------
set REMOTE_AS   130537
set TAG         "EEM-BGP-130537"

set errorInfo ""
global cli1

# ----------------------------
# Helpers
# ----------------------------
proc log_info {s} {
    action_syslog priority info msg $s
}
proc log_warn {s} {
    action_syslog priority warning msg $s
}
proc log_err {s} {
    action_syslog priority err msg $s
}

# ----------------------------
# Read syslog message
# ----------------------------
array set ei [event_reqinfo]
set msg ""
if {[info exists ei(msg)]} {
    set msg $ei(msg)
} else {
    if {[info exists ei(syslog_msg)]} {
        set msg $ei(syslog_msg)
    } else {
        if {[info exists ei(message)]} {
            set msg $ei(message)
        }
    }
}
set msg [string trim $msg]

# Prevent recursion
if {[string first $TAG $msg] >= 0} {
    exit 0
}

# Must be bgp ADJCHANGE_DETAIL line
if {![regexp {:\s*bgp\[[0-9]+\]:\s*%ROUTING-BGP-5-ADJCHANGE_DETAIL} $msg]} {
    exit 0
}

# Only v4 unicast events
if {![regexp {AFI/SAFI:\s*1/1} $msg]} { exit 0 }

# Only for this remote AS
if {![regexp "\\(AS:\\s*${REMOTE_AS}\\)" $msg]} { exit 0 }

# Parse neighbor + Up/Down from syslog (for printing)
set ip ""
set st ""
if {![regexp -nocase {neighbor\s+([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\s+(Up|Down)} $msg -> ip st]} {
    log_err "$TAG: parse_failed msg='$msg'"
    exit 0
}
set st [string toupper $st]

# ----------------------------
# CLI open/close
# ----------------------------
proc open_cli {} {
    global cli1
    global errorInfo
    if [catch {cli_open} result] {
        return 0
    }
    array set cli1 $result
    return 1
}

proc close_cli {} {
    global cli1
    global errorInfo
    catch {cli_close $cli1(fd) $cli1(tty_id)}
}

# ----------------------------
# Snapshot using:
#   show bgp summary | include <REMOTE_AS>
# UP definition: "State/PfxRcd" column is numeric (Established)
# DOWN definition: "State/PfxRcd" column is non-numeric (Idle/Active/etc)
# ----------------------------
proc snapshot_bgp_summary {} {
    global cli1
    global REMOTE_AS

    set cmd "show bgp summary | include ${REMOTE_AS}"
    if [catch {cli_exec $cli1(fd) $cmd} out] {
        return -code error "cli_exec_failed"
    }

    set tracked 0
    set up 0
    set down 0
    set up_ips ""
    set down_ips ""

    foreach line [split $out "\n"] {
        set line [string trim $line]
        if {$line eq ""} { continue }

        # Summary lines start with neighbor IPv4
        if {![regexp {^([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\s+} $line -> nbr]} {
            continue
        }

        # Must contain the remote AS field
        if {![regexp "\\s${REMOTE_AS}\\s" $line]} {
            continue
        }

        set fields [split $line]
        if {[llength $fields] < 3} { continue }

        # State/PfxRcd is the last column (numeric if established)
        set last [lindex $fields end]
        incr tracked

        if {[regexp {^[0-9]+$} $last]} {
            incr up
            append up_ips "$nbr "
        } else {
            incr down
            append down_ips "$nbr "
        }
    }

    set up_ips [string trim $up_ips]
    set down_ips [string trim $down_ips]

    return [list $tracked $up $down $up_ips $down_ips]
}

# ----------------------------
# Main
# ----------------------------
# Log the triggering event first (so you know it matched)
log_warn "$TAG: TRIGGER syslog_event ip=$ip state=$st"

if {![open_cli]} {
    log_err "$TAG: CLI open failed"
    exit 0
}

set snap ""
if {[catch {set snap [snapshot_bgp_summary]} err]} {
    log_err "$TAG: snapshot_failed ($err)"
    close_cli
    exit 0
}

close_cli

set tracked [lindex $snap 0]
set up      [lindex $snap 1]
set down    [lindex $snap 2]
set up_ips  [lindex $snap 3]
set dn_ips  [lindex $snap 4]

log_info "$TAG: SNAPSHOT TRACKED=$tracked UP=$up DOWN=$down"
log_info "$TAG: UP_NEIGHBORS count=$up ips='$up_ips'"
log_info "$TAG: DOWN_NEIGHBORS count=$down ips='$dn_ips'"

exit 0
