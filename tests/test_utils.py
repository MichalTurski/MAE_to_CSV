import pytest
from igcogito.aim_category import utils

SYSNET_NAMES = [
    ("{wybierać_się.1(36:ruch), wyprawiać_się.1(36:ruch), uderzać.11(36:ruch)}", 36)
]


@pytest.mark.parametrize("synset_name, domain_id", SYSNET_NAMES)
def test_get_synset_domain(synset_name, domain_id):
    ret_domain_id = utils.get_synset_domain(synset_name)
    assert domain_id == ret_domain_id


