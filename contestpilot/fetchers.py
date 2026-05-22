import logging
import requests
import json
import datetime
from typing import List, Dict, Any, Optional

from .models import Contest
from .database import get_preference, get_api_cache, set_api_cache, save_contest, save_ranking
from .utils import utc_now_iso
from .ranking import rank_contest

logger = logging.getLogger(__name__)

CACHE_EXPIRY_SECONDS = 3600  # 1 hour

# ... [skipping cache/fetch functions unchanged for brevity, but I should use a robust replace for the exact lines]

CACHE_EXPIRY_SECONDS = 3600  # 1 hour

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def get_requests_session() -> requests.Session:
    session = requests.Session()
    # Retry on 429, 500, 502, 503, 504
    retry = Retry(
        total=3,
        backoff_factor=1, # 1s, 2s, 4s...
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def fetch_with_cache(url: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, str]] = None) -> Optional[Dict[str, Any]]:
    """Fetches a URL with a simple SQLite cache and robust retries."""
    cache_key = url
    if params:
        cache_key += "?" + "&".join(f"{k}={v}" for k, v in sorted(params.items()))
    
    cached = get_api_cache(cache_key)
    if cached:
        try:
            fetched_at = datetime.datetime.fromisoformat(cached['fetched_at'])
            if (datetime.datetime.now(datetime.timezone.utc) - fetched_at).total_seconds() < CACHE_EXPIRY_SECONDS:
                logger.debug(f"Cache hit for {cache_key}")
                return json.loads(cached['response'])
        except Exception as e:
            logger.warning(f"Error reading cache for {cache_key}: {e}")

    if not headers:
        headers = {}
    if "User-Agent" not in headers:
        headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

    try:
        logger.info(f"Fetching from network: {url}")
        session = get_requests_session()
        response = session.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        set_api_cache(cache_key, json.dumps(data), utc_now_iso())
        return data
    except Exception as e:
        logger.error(f"Failed to fetch {url}: {e}")
        return None

class BaseFetcher:
    platform_name = "Unknown"

    def fetch(self) -> List[Contest]:
        """Fetch and return normalized contests."""
        raise NotImplementedError

class CodeforcesFetcher(BaseFetcher):
    platform_name = "codeforces"

    def fetch(self) -> List[Contest]:
        enabled = get_preference('platforms') or ""
        if 'codeforces' not in enabled:
            return []
            
        url = "https://codeforces.com/api/contest.list"
        data = fetch_with_cache(url)
        contests = []
        
        if data and data.get('status') == 'OK':
            for item in data.get('result', []):
                if item.get('phase') == 'BEFORE':
                    source_id = str(item.get('id'))
                    duration = item.get('durationSeconds', 0)
                    start_ts = item.get('startTimeSeconds', 0)
                    if start_ts > 0:
                        start_time = datetime.datetime.fromtimestamp(start_ts, datetime.timezone.utc)
                        end_time = start_time + datetime.timedelta(seconds=duration)
                        
                        c = Contest(
                            id=f"codeforces_{source_id}",
                            source_id=source_id,
                            name=item.get('name'),
                            platform="codeforces",
                            start_time=start_time.isoformat(),
                            end_time=end_time.isoformat(),
                            duration_seconds=duration,
                            url=f"https://codeforces.com/contest/{source_id}",
                            status="UPCOMING"
                        )
                        contests.append(c)
        return contests


class AtCoderFetcher(BaseFetcher):
    platform_name = "atcoder"

    def fetch(self) -> List[Contest]:
        enabled = get_preference('platforms') or ""
        if 'atcoder' not in enabled:
            return []
            
        # Kenkoooo is stable and community-maintained. Official AtCoder API requires scraping.
        url = "https://kenkoooo.com/atcoder/resources/contests.json"
        data = fetch_with_cache(url)
        contests = []
        
        if data:
            now_ts = datetime.datetime.now(datetime.timezone.utc).timestamp()
            for item in data:
                start_ts = item.get('start_epoch_second', 0)
                if start_ts > now_ts:
                    source_id = str(item.get('id'))
                    duration = item.get('duration_second', 0)
                    start_time = datetime.datetime.fromtimestamp(start_ts, datetime.timezone.utc)
                    end_time = start_time + datetime.timedelta(seconds=duration)
                    
                    c = Contest(
                        id=f"atcoder_{source_id}",
                        source_id=source_id,
                        name=item.get('title'),
                        platform="atcoder",
                        start_time=start_time.isoformat(),
                        end_time=end_time.isoformat(),
                        duration_seconds=duration,
                        url=f"https://atcoder.jp/contests/{source_id}",
                        status="UPCOMING"
                    )
                    contests.append(c)
        return contests

class LeetCodeFetcher(BaseFetcher):
    platform_name = "leetcode"

    def fetch(self) -> List[Contest]:
        enabled = get_preference('platforms') or ""
        if 'leetcode' not in enabled:
            return []
            
        url = "https://leetcode.com/graphql"
        query = {
            "query": "{ allContests { title titleSlug startTime duration isVirtual } }"
        }
        
        session = get_requests_session()
        try:
            response = session.post(url, json=query, timeout=10)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return []
            
        contests = []
        now_ts = datetime.datetime.now(datetime.timezone.utc).timestamp()
        
        if data and 'data' in data and 'allContests' in data['data']:
            for item in data['data']['allContests']:
                if not item.get('isVirtual') and item.get('startTime', 0) > now_ts:
                    source_id = item.get('titleSlug')
                    duration = item.get('duration', 0)
                    start_ts = item.get('startTime', 0)
                    
                    start_time = datetime.datetime.fromtimestamp(start_ts, datetime.timezone.utc)
                    end_time = start_time + datetime.timedelta(seconds=duration)
                    
                    c = Contest(
                        id=f"leetcode_{source_id}",
                        source_id=source_id,
                        name=item.get('title'),
                        platform="leetcode",
                        start_time=start_time.isoformat(),
                        end_time=end_time.isoformat(),
                        duration_seconds=duration,
                        url=f"https://leetcode.com/contest/{source_id}",
                        status="UPCOMING"
                    )
                    contests.append(c)
        return contests

class CodeChefFetcher(BaseFetcher):
    platform_name = "codechef"

    def fetch(self) -> List[Contest]:
        enabled = get_preference('platforms') or ""
        if 'codechef' not in enabled:
            return []
            
        url = "https://www.codechef.com/api/list/contests/all"
        data = fetch_with_cache(url)
        contests = []
        
        if data and 'future_contests' in data:
            for item in data['future_contests']:
                source_id = item.get('contest_code')
                try:
                    start_time = datetime.datetime.fromisoformat(item.get('contest_start_date_iso'))
                    end_time = datetime.datetime.fromisoformat(item.get('contest_end_date_iso'))
                    duration = int((end_time - start_time).total_seconds())
                except Exception:
                    continue
                    
                c = Contest(
                    id=f"codechef_{source_id}",
                    source_id=source_id,
                    name=item.get('contest_name'),
                    platform="codechef",
                    start_time=start_time.isoformat(),
                    end_time=end_time.isoformat(),
                    duration_seconds=duration,
                    url=f"https://www.codechef.com/{source_id}",
                    status="UPCOMING"
                )
                contests.append(c)
        return contests

def sync_all_fetchers():
    """Run all fetchers, store results, and prevent duplicates via DB upsert."""
    from .database import get_connection, queue_notification
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM contests WHERE status = 'UPCOMING'")
    old_upcoming = {r['id']: r['name'] for r in cursor.fetchall()}
    conn.close()

    fetchers = [
        CodeforcesFetcher(),
        LeetCodeFetcher(),
        CodeChefFetcher(),
        AtCoderFetcher()
    ]
    
    total_synced = 0
    new_upcoming = set()
    
    for fetcher in fetchers:
        logger.info(f"Syncing platform: {fetcher.platform_name}...")
        try:
            contests = fetcher.fetch()
            for c in contests:
                save_contest(c)
                priority, reason = rank_contest(c)
                save_ranking(c.id, priority, reason)
                new_upcoming.add(c.id)
            total_synced += len(contests)
            if contests:
                logger.info(f"  -> Saved {len(contests)} upcoming contests.")
        except Exception as e:
            logger.error(f"  -> Error fetching from {fetcher.platform_name}: {e}")
            
    # Detect cancellations
    canceled_ids = set(old_upcoming.keys()) - new_upcoming
    if canceled_ids:
        from .database import log_history
        for cid in canceled_ids:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT name, platform, url, start_time FROM contests WHERE id = ?", (cid,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                import datetime
                from tzlocal import get_localzone
                try:
                    start_dt = datetime.datetime.fromisoformat(row['start_time'].replace('Z', '+00:00'))
                    local_tz = get_localzone()
                    start_local = start_dt.astimezone(local_tz).strftime('%b %d, %I:%M %p')
                except Exception:
                    start_local = row['start_time']
                
                msg = f"Contest canceled or removed: {row['name']}\nPlatform: {row['platform'].title()}\nScheduled for: {start_local}\nLink: {row['url']}"
            else:
                msg = f"Contest canceled or removed: {old_upcoming[cid]}"
                
            log_history(cid, 'STATUS', 'UPCOMING', 'CANCELED')
            queue_notification('CANCELED', cid, msg)
            
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE contests SET status = 'CANCELED' WHERE id = ?", (cid,))
            conn.commit()
            conn.close()
            
    from .analytics import log_sync
    log_sync(total_synced, 0, 0, len(canceled_ids))
    logger.info(f"Total {total_synced} contests successfully parsed and saved.")
