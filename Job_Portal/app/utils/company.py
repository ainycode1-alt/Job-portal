import logging
import re
from urllib.parse import urlparse
import httpx

logger = logging.getLogger(__name__)

def extract_domain(url: str) -> str:
    """Extract domain name from a website URL."""
    if not url:
        return ""
    try:
        url_str = url.strip()
        if not url_str.startswith(("http://", "https://")):
            url_str = "https://" + url_str
        parsed = urlparse(url_str)
        domain = parsed.netloc
        if domain.startswith("www."):
            domain = domain[4:]
        return domain
    except Exception as e:
        logger.warning(f"Failed to parse domain from url {url}: {e}")
        return ""

async def fetch_wikidata_company_data(company_name: str) -> dict:
    """
    Search Wikidata for a company by name and fetch its headquarters
    location and inception (founding year) if available.
    """
    result = {
        "hq_location": None,
        "founded_year": None
    }
    
    if not company_name:
        return result

    headers = {
        "User-Agent": "JobPortalApp/1.0 (contact: info@jobportal.com)"
    }
    
    try:
        async with httpx.AsyncClient(headers=headers, timeout=5.0) as client:
            # 1. Search Wikidata for the entity
            search_url = "https://www.wikidata.org/w/api.php"
            params = {
                "action": "wbsearchentities",
                "search": company_name,
                "language": "en",
                "format": "json",
                "type": "item"
            }
            
            r = await client.get(search_url, params=params)
            r.raise_for_status()
            search_results = r.json().get("search", [])
            if not search_results:
                return result
                
            entity_id = None
            # Find the most likely company entity matching the label
            for item in search_results:
                desc = item.get("description", "").lower()
                if any(kw in desc for kw in ["company", "corporation", "enterprise", "manufacturer", "retailer", "business"]):
                    entity_id = item.get("id")
                    break
            
            if not entity_id:
                entity_id = search_results[0].get("id")
                
            # 2. Fetch Entity Claims
            entity_url = f"https://www.wikidata.org/wiki/Special:EntityData/{entity_id}.json"
            r_entity = await client.get(entity_url)
            r_entity.raise_for_status()
            
            entity_data = r_entity.json().get("entities", {}).get(entity_id, {})
            claims = entity_data.get("claims", {})
            
            # Extract Founding Year (P571 - inception)
            inception_claims = claims.get("P571", [])
            if inception_claims:
                time_val = inception_claims[0].get("mainsnak", {}).get("datavalue", {}).get("value", {}).get("time")
                if time_val:
                    # Format: "+1998-09-04T00:00:00Z"
                    match = re.search(r"\d{4}", time_val)
                    if match:
                        result["founded_year"] = int(match.group())
                        
            # Extract Headquarters location (P159)
            hq_claims = claims.get("P159", [])
            if hq_claims:
                hq_entity_id = hq_claims[0].get("mainsnak", {}).get("datavalue", {}).get("value", {}).get("id")
                if hq_entity_id:
                    # Query the label of the location
                    hq_label_url = "https://www.wikidata.org/w/api.php"
                    hq_params = {
                        "action": "wbgetentities",
                        "ids": hq_entity_id,
                        "props": "labels",
                        "languages": "en",
                        "format": "json"
                    }
                    r_hq = await client.get(hq_label_url, params=hq_params)
                    r_hq.raise_for_status()
                    result["hq_location"] = r_hq.json().get("entities", {}).get(hq_entity_id, {}).get("labels", {}).get("en", {}).get("value")
                    
    except Exception as e:
        logger.warning(f"Wikidata auto-fetch failed for {company_name}: {e}")
        
    return result
