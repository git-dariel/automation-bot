export type SampleProfile = {
  id: string;
  email: string;
  clinicianName: string;
  studentNumber: string;
  scheduledDay: string;
  shiftSchedule: string;
  department: string;
  timeInterval: string;
};

const samples = [
  [
    "alex.rivera@example.com",
    "Alex Rivera",
    "TEST-2026-001",
    "Monday",
    "8-12 AM shift",
    "OD / OP",
    "4 hrs",
  ],
  [
    "jamie.santos@example.com",
    "Jamie Santos",
    "TEST-2026-002",
    "Wednesday",
    "12-4 PM shift",
    "Endodontics",
    "2hrs",
  ],
  [
    "morgan.reyes@example.com",
    "Morgan Reyes",
    "TEST-2026-003",
    "Friday",
    "4-8 PM shift",
    "Orthodontics",
    "1hr",
  ],
  [
    "taylor.cruz@example.com",
    "Taylor Cruz",
    "TEST-2026-004",
    "Tuesday",
    "8-12 AM shift",
    "Prothodontics",
    "2hrs",
  ],
  [
    "casey.garcia@example.com",
    "Casey Garcia",
    "TEST-2026-005",
    "Thursday",
    "12-4 PM shift",
    "Operative Dentistry",
    "1hr",
  ],
  [
    "jordan.lim@example.com",
    "Jordan Lim",
    "TEST-2026-006",
    "Monday",
    "4-8 PM shift",
    "Periodontics",
    "4 hrs",
  ],
  [
    "riley.mendoza@example.com",
    "Riley Mendoza",
    "TEST-2026-007",
    "Tuesday",
    "8-12 AM shift",
    "Oral Sugery",
    "2hrs",
  ],
  [
    "avery.flores@example.com",
    "Avery Flores",
    "TEST-2026-008",
    "Wednesday",
    "12-4 PM shift",
    "Pediatrics",
    "1hr",
  ],
  [
    "quinn.navarro@example.com",
    "Quinn Navarro",
    "TEST-2026-009",
    "Thursday",
    "4-8 PM shift",
    "TYPO",
    "4 hrs",
  ],
  [
    "drew.velasco@example.com",
    "Drew Velasco",
    "TEST-2026-010",
    "Friday",
    "8-12 AM shift",
    "OD / OP",
    "2hrs",
  ],
] as const;

export function buildSampleProfiles(): SampleProfile[] {
  return samples.map(
    ([email, name, studentNumber, day, shift, department, interval], index) => ({
      id: `clinician-${index + 1}`,
      email,
      clinicianName: name,
      studentNumber,
      scheduledDay: day,
      shiftSchedule: shift,
      department,
      timeInterval: interval,
    }),
  );
}
