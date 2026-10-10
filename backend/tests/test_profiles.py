from backend.app.profiles import build_sample_profiles


def test_profiles_are_fabricated_unique_and_cover_requested_choices():
    profiles = build_sample_profiles()

    assert len(profiles) == 10
    assert len({profile.id for profile in profiles}) == 10
    assert len({profile.email for profile in profiles}) == 10
    assert len({profile.student_number for profile in profiles}) == 10
    assert {profile.scheduled_day for profile in profiles} == {
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
    }
    assert {profile.shift_schedule for profile in profiles} == {
        "8-12 AM shift",
        "12-4 PM shift",
        "4-8 PM shift",
    }
    assert {profile.time_interval for profile in profiles} == {"4 hrs", "2hrs", "1hr"}
    assert {profile.department for profile in profiles} == {
        "OD / OP",
        "Prothodontics",
        "Endodontics",
        "Operative Dentistry",
        "Periodontics",
        "Oral Sugery",
        "Orthodontics",
        "Pediatrics",
        "TYPO",
    }
    assert all(profile.student_number.startswith("TEST-2026-") for profile in profiles)
    assert all(profile.email.endswith("@example.com") for profile in profiles)
