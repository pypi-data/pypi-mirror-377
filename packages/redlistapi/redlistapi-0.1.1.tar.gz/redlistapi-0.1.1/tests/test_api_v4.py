import pytest
import dotenv
import redlistapi


token = dotenv.dotenv_values(dotenv.find_dotenv('../.env')).get('REDLIST_API_TOKEN')


# Test assid, taxid, binomial endpoints
def test_assessment_id():
    redlistapi.api.v4.assessment.by_assessment_id(token=token, assessment_id=247624660)
def test_sis_id():
    redlistapi.api.v4.taxa.sis.by_sis_id(token=token, sis_id=3746)
def test_scientific_name():
    redlistapi.api.v4.taxa.scientific_name(token=token, species_name='Canis', genus_name='lupus')

# Test taxonomic lists
def test_kingdom_list():
    redlistapi.api.v4.taxa.kingdom.list(token=token)
def test_phylum_list():
    redlistapi.api.v4.taxa.phylum.list(token=token)
def test_class_list():
    redlistapi.api.v4.taxa.class_.list(token=token)
def test_order_list():
    redlistapi.api.v4.taxa.order.list(token=token)
def test_family_list():
    redlistapi.api.v4.taxa.family.list(token=token)

# Test taxonomic catalogs
def test_kingdom_name():
    redlistapi.api.v4.taxa.kingdom.by_kingdom_name(token=token,
        kingdom_name=[*redlistapi.api.v4.taxa.kingdom.list(token=token).json().values()][0][0])
def test_phylum_name():
    redlistapi.api.v4.taxa.phylum.by_phylum_name(token=token,
        phylum_name=[*redlistapi.api.v4.taxa.phylum.list(token=token).json().values()][0][0])
def test_class_name():
    redlistapi.api.v4.taxa.class_.by_class_name(token=token,
        class_name=[*redlistapi.api.v4.taxa.class_.list(token=token).json().values()][0][0])
def test_order_name():
    redlistapi.api.v4.taxa.order.by_order_name(token=token,
        order_name=[*redlistapi.api.v4.taxa.order.list(token=token).json().values()][0][0])
def test_family_name():
    redlistapi.api.v4.taxa.family.by_family_name(token=token,
        family_name=[*redlistapi.api.v4.taxa.family.list(token=token).json().values()][0][0])

# Test PE/PEW lists
def test_possibly_extinct():
    redlistapi.api.v4.taxa.possibly_extinct(token=token)
def test_possibly_extinct_in_the_wild():
    redlistapi.api.v4.taxa.possibly_extinct_in_the_wild(token=token)


if __name__ == "__main__":
    import pytest
    pytest.main([__file__])