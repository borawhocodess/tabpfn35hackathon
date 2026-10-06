// exports apple calendar events as tsv, read only
//
//   swiftc scripts/export.swift -o workdir/export
//   workdir/export 2024-09-01 2027-07-01 > workdir/exports/events-2026-09-22.tsv
//   workdir/export 2026-09-22 2026-10-07 > workdir/exports/events-2026-10-06.tsv

import EventKit
import Foundation

let arguments = CommandLine.arguments

if arguments.count != 3 {
  print("usage: export <start yyyy-MM-dd> <end yyyy-MM-dd>")
  exit(1)
}

let store = EKEventStore()
let semaphore = DispatchSemaphore(value: 0)
store.requestFullAccessToEvents { _, _ in semaphore.signal() }
semaphore.wait()

let skip: Set<String> = ["Birthdays", "Deutsche Feiertage", "Siri Suggestions", "Scheduled Reminders", "Geburtstage"]
let calendars = store.calendars(for: .event).filter { !skip.contains($0.title) }

let day = DateFormatter()
day.dateFormat = "yyyy-MM-dd"
let minute = DateFormatter()
minute.dateFormat = "yyyy-MM-dd HH:mm"

guard var start = day.date(from: arguments[1]), let end = day.date(from: arguments[2]) else {
  print("dates must be yyyy-MM-dd")
  exit(1)
}

func clean(_ text: String?) -> String {
  (text ?? "").replacingOccurrences(of: "\n", with: " ").replacingOccurrences(of: "\t", with: " ")
}

print("start\tend\tcalendar\ttitle\tallday\tnotes")

// month by month, eventkit limits how long one search can be
while start < end {
  let next = min(Calendar.current.date(byAdding: .month, value: 1, to: start)!, end)
  let events = store.events(matching: store.predicateForEvents(withStart: start, end: next, calendars: calendars))

  for event in events where event.startDate >= start {
    print("\(minute.string(from: event.startDate))\t\(minute.string(from: event.endDate))\t\(event.calendar.title)\t\(clean(event.title))\t\(event.isAllDay)\t\(clean(event.notes))")
  }

  start = next
}
