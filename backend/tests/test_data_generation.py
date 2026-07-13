from app.data_store import DEMO_ARCHETYPES, get_data_store


def test_twenty_msmes_loaded():
    store = get_data_store()
    assert len(store.master) == 20
    assert len(store.public) == 20
    assert len(store.consent) == 20


def test_all_five_demo_archetypes_present():
    store = get_data_store()
    archetypes_seen = {m.archetype.value for m in store.master.values()}
    assert DEMO_ARCHETYPES.issubset(archetypes_seen)


def test_every_msme_has_matching_public_and_consent_records():
    store = get_data_store()
    for msme_id in store.master:
        assert msme_id in store.public
        assert msme_id in store.consent


def test_at_least_two_tier2_tier3_cities_present():
    store = get_data_store()
    tier2_3 = {
        "Coimbatore", "Surat", "Indore", "Nagpur", "Madurai", "Rajkot", "Vijayawada",
        "Jaipur", "Lucknow", "Bhopal", "Nashik", "Kochi", "Guwahati", "Patna",
        "Ludhiana", "Vadodara", "Amritsar", "Mysore", "Chandigarh", "Visakhapatnam",
    }
    cities = {m.city for m in store.master.values()}
    assert cities.issubset(tier2_3)
