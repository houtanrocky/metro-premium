"""Versioned price interpretation with an explicit evidence source and scope."""
import yaml
from .provenance import REVISION

def load_price_contract(path):
    contract=yaml.safe_load(path.read_text(encoding='utf-8'))
    expected={'city_slug':'tehran','cat2_slug':'residential-sell','cat3_slug':'apartment-sell','price_mode':'مقطوع'}
    if contract.get('repository')!='divarofficial/real_estate_ads' or contract.get('revision')!=REVISION:
        raise ValueError('Price interpretation does not cover this pinned dataset revision')
    if contract.get('scope')!=expected:
        raise ValueError('Price interpretation does not cover the analytical population')
    if contract.get('denomination')!='toman' or contract.get('price_basis')!='total_apartment_asking_price':
        raise ValueError('Unsupported monetary unit or price basis')
    if contract.get('total_price_verified') is not True or contract.get('per_m2_enabled') is not True:
        raise ValueError('Price interpretation is not enabled')
    if contract.get('verification_source')!='owner_confirmation' or not contract.get('evidence'):
        raise ValueError('Missing price interpretation evidence')
    if contract.get('publisher_documentation_verified') is not False:
        raise ValueError('Owner confirmation must not be relabeled as publisher verification')
    return contract
