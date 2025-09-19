# -*- coding: utf-8 -*-
"""
Constitute Project 憲法爬蟲與查詢系統（MCP版本）
- 修正 get_constitutions_list：先嘗試 JSON，不合則回退 HTML A–Z 清單解析
- 檔名消毒：解決 Windows 非法字元（? 等）
- 抓取憲法頁時固定 ?lang=en，並以乾淨 slug 記錄
- 新增 Topic 搜尋（constopicsearch / sectionstopicsearch），解析片段 HTML
- 互動式主題搜尋選單
- 進階 log：每次請求帶 req_id、耗時、狀態、bytes、JSON 解析狀態、片段解析等
"""

from __future__ import annotations

import requests
import json
import time
import csv
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
from datetime import datetime
import logging
import re
from difflib import get_close_matches
import uuid
from typing import List, Tuple


# ---------- Logging 輔助 Filter，確保每條 log 都有 run_id/req_id ----------
class _ContextFilter(logging.Filter):
    def __init__(self, run_id: str):
        super().__init__()
        self._run_id = run_id

    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "run_id"):
            record.run_id = self._run_id
        if not hasattr(record, "req_id"):
            record.req_id = "-"
        return True


class ConstituteScraper:
    # 可選的國名別名，改善互動搜尋體驗
    ALIASES = {
        "taiwan": "Taiwan (Republic of China)",
        "roc": "Taiwan (Republic of China)",
        "south korea": "Korea (Republic of)",  # ROK
        "republic of korea": "Korea (Republic of)",
        "north korea": "Korea (Democratic People's Republic of)",  # DPRK
        "dprk": "Korea (Democratic People's Republic of)",
        "uk": "United Kingdom",
        "uae": "United Arab Emirates",
        "usa": "United States of America",
    }

    def __init__(self, delay=1):
        """
        初始化爬蟲
        :param delay: 請求間隔時間（秒）
        """
        self.base_url = "https://constituteproject.org"
        self.delay = delay
        self.session = requests.Session()
        self.constitutions_list = None  # 緩存憲法列表

        # 設置請求頭，模擬瀏覽器
        self.session.headers.update(
            {
                "accept": "application/json, text/plain, */*",
                "accept-language": "zh-TW,zh;q=0.9,en;q=0.8,en-US;q=0.7,ja;q=0.6,zh-CN;q=0.5",
                "sec-ch-ua": '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
                "sec-ch-ua-mobile": "?1",
                "sec-ch-ua-platform": '"Android"',
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Mobile Safari/537.36",
            }
        )

        # ---- Logging 設定（同時輸出到 console 與檔案 constitute.log）----
        self.run_id = uuid.uuid4().hex[:8]  # 每次程式啟動給一個 run 標識
        self.req_seq = 0  # 遞增的請求序號

        self.logger = logging.getLogger("ConstituteScraper")
        self.logger.setLevel(logging.DEBUG)  # 如需安靜些可改成 logging.INFO

        if not self.logger.handlers:
            fmt = logging.Formatter(
                "%(asctime)s - %(levelname)s - %(name)s "
                "- run=%(run_id)s req=%(req_id)s - %(message)s"
            )

            ctx = _ContextFilter(self.run_id)

            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)
            ch.setFormatter(fmt)
            ch.addFilter(ctx)
            self.logger.addHandler(ch)

            fh = logging.FileHandler("constitute.log", encoding="utf-8")
            fh.setLevel(logging.DEBUG)
            fh.setFormatter(fmt)
            fh.addFilter(ctx)
            self.logger.addHandler(fh)

    # ------------------ Logging 小工具 ------------------
    def _make_logger(self, req_id: str | None = None):
        """為當前動作建立帶 req_id 的 LoggerAdapter。"""
        return logging.LoggerAdapter(self.logger, {"req_id": req_id or "-"})

    def _next_req_id(self) -> str:
        self.req_seq += 1
        return f"{self.run_id}-{self.req_seq:04d}"

    # ------------------ 公用工具 ------------------
    def sanitize_filename(self, name: str, replacement: str = "_") -> str:
        """Windows 安全檔名；同時記 log 若有變更。"""
        original = name
        name = name.split("?")[0]
        name = re.sub(r'[<>:"/\\|?*]', replacement, name)
        name = name.rstrip(" .")
        reserved = {
            "CON",
            "PRN",
            "AUX",
            "NUL",
            "COM1",
            "COM2",
            "COM3",
            "COM4",
            "COM5",
            "COM6",
            "COM7",
            "COM8",
            "COM9",
            "LPT1",
            "LPT2",
            "LPT3",
            "LPT4",
            "LPT5",
            "LPT6",
            "LPT7",
            "LPT8",
            "LPT9",
        }
        if name.upper() in reserved:
            name = f"_{name}_"
        name = name[:120]
        if name != original:
            self._make_logger().debug('sanitize filename: "%s" -> "%s"', original, name)
        return name

    def _request_json(self, path: str, params: dict | None = None):
        """GET JSON with 觀測點 log：URL/params/status/elapsed/bytes/JSON 解析狀態。"""
        url = f"{self.base_url}{path}"
        req_id = self._next_req_id()
        lg = self._make_logger(req_id)
        t0 = time.time()
        lg.info("HTTP GET %s params=%s", url, params or {})
        try:
            r = self.session.get(url, params=params or {}, timeout=20)
            elapsed = (
                r.elapsed.total_seconds()
                if getattr(r, "elapsed", None)
                else (time.time() - t0)
            )
            lg.debug(
                "response status=%s elapsed=%.3fs bytes=%s content-type=%s",
                r.status_code,
                elapsed,
                len(r.content),
                r.headers.get("Content-Type"),
            )
            r.raise_for_status()
            try:
                data = r.json()
                size = (
                    len(data)
                    if isinstance(data, list)
                    else (len(data.keys()) if isinstance(data, dict) else "?")
                )
                lg.debug("json_ok type=%s size=%s", type(data).__name__, size)
                return data
            except json.JSONDecodeError as je:
                sample = r.text[:300].replace("\n", " ")
                lg.error("json_decode_error: %s; sample=%r", je, sample)
                return None
        except Exception as e:
            lg.exception("request_failed: %s", e)
            return None

    # ------------------ 清單取得（JSON -> HTML fallback） ------------------
    def get_constitutions_list(self):
        """
        取得憲法清單；優先嘗試 JSON，失敗則回退用 /constitutions 頁面解析。
        傳回的每筆至少會有: id, country, title_long
        """
        if self.constitutions_list is not None:
            return self.constitutions_list

        lg = self._make_logger()
        # 1) 先試 playlists JSON
        try:
            lg.info("get_constitutions_list: try playlists JSON")
            url = f"{self.base_url}/service/playlists?lang=en"
            resp = self.session.get(url, timeout=20)
            lg.debug(
                "playlists status=%s bytes=%d", resp.status_code, len(resp.content)
            )
            resp.raise_for_status()
            data = resp.json()

            if isinstance(data, dict) and "constitutions" in data:
                self.constitutions_list = data["constitutions"]
                lg.info(
                    "get_constitutions_list(JSON): %d item(s)",
                    len(self.constitutions_list),
                )
                return self.constitutions_list

            # 若是 list 或其他型態，視為不可用 → fallback
            raise ValueError(
                f"unexpected playlists payload type: {type(data).__name__}"
            )

        except Exception as e:
            lg.warning(
                "get_constitutions_list: JSON not usable, fallback to HTML (%s)", e
            )

        # 2) 回退：抓 /constitutions A–Z 清單頁並解析所有憲法連結
        try:
            html_url = f"{self.base_url}/constitutions?lang=en"
            r = self.session.get(html_url, timeout=20)
            lg.debug(
                "constitutions page status=%s bytes=%d", r.status_code, len(r.content)
            )
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")

            items = []
            # 找所有 /constitution/<slug> 連結
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if href.startswith("/constitution/"):
                    const_id = href.split("/")[-1].split("?")[0]  # 去 query
                    title = a.get_text(strip=True)
                    if not const_id or not title:
                        continue

                    # 以顯示文字暫定國名（保留完整 title）
                    country = title  # 如需更乾淨可切年份資訊

                    items.append(
                        {
                            "id": const_id,
                            "country": country,
                            "title_long": title,
                            "year_enacted": None,
                            "in_force": None,
                            "region": None,
                            "word_length": None,
                        }
                    )

            # 去重（以 id 為主）
            seen = set()
            uniq = []
            for it in items:
                if it["id"] not in seen:
                    seen.add(it["id"])
                    uniq.append(it)

            self.constitutions_list = uniq
            lg.info(
                "get_constitutions_list(HTML): %d item(s)", len(self.constitutions_list)
            )
            return self.constitutions_list

        except Exception as e:
            self.logger.error(f"HTML 解析憲法清單失敗：{e}")
            return []

    def find_constitution_by_country(self, country_name, exact_match=False):
        """
        根據國家名稱查找憲法
        :param country_name: 國家名稱
        :param exact_match: 是否精確匹配
        :return: 匹配的憲法列表
        """
        constitutions = self.get_constitutions_list()
        if not constitutions:
            return []

        # 別名映射
        country_name_lower = country_name.lower().strip()
        mapped = self.ALIASES.get(country_name_lower, None)
        query_name = mapped or country_name

        matches = []
        q_lower = query_name.lower().strip()

        for constitution in constitutions:
            constitution_country = (constitution.get("country") or "").lower()
            if not constitution_country:
                continue

            if exact_match:
                if constitution_country == q_lower:
                    matches.append(constitution)
            else:
                if (q_lower in constitution_country) or (
                    constitution_country in q_lower
                ):
                    matches.append(constitution)

        return matches

    # ------------------ 下載與解析憲法 ------------------
    def scrape_constitution_content(self, constitution_id):
        """
        爬取特定憲法的內容
        :param constitution_id: 憲法ID
        :return: 解析後的憲法內容
        """
        try:
            slug = constitution_id.split("?")[0]
            url = f"{self.base_url}/constitution/{slug}?lang=en"

            lg = self._make_logger()
            lg.info("scrape_constitution url=%s", url)

            # 更新請求頭為HTML請求
            headers = {
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "accept-language": "zh-TW,zh;q=0.9,en;q=0.8,en-US;q=0.7,ja;q=0.6,zh-CN;q=0.5",
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "same-origin",
                "sec-fetch-user": "?1",
                "upgrade-insecure-requests": "1",
            }

            response = self.session.get(url, headers=headers, timeout=30)
            lg.debug(
                "scrape_constitution status=%s bytes=%d",
                response.status_code,
                len(response.content),
            )
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            # 解析憲法內容
            constitution_data = self.parse_constitution_html(soup, slug)

            lg.info(
                "scrape_constitution parsed: chapters=%d articles=%d title=%r",
                len(constitution_data.get("chapters", [])),
                len(constitution_data.get("articles", [])),
                constitution_data.get("title"),
            )

            return constitution_data

        except requests.RequestException as e:
            self.logger.error(f"爬取憲法 {constitution_id} 失敗: {e}")
            return None
        except Exception as e:
            self.logger.error(f"解析憲法 {constitution_id} 失敗: {e}")
            return None

    def normalize_article_number(self, article_title):
        """
        正規化條文編號
        :param article_title: 條文標題
        :return: (條文編號, 清理後的標題)
        """
        patterns = [
            r"Article\s+(\d+(?:-\d+)?)",  # Article 1, Article 1-1
            r"Art\.?\s+(\d+(?:-\d+)?)",  # Art. 1, Art 1-1
            r"Section\s+(\d+(?:-\d+)?)",  # Section 1
            r"Sec\.?\s+(\d+(?:-\d+)?)",  # Sec. 1
            r"^(\d+(?:-\d+)?)\.?",  # 1., 1-1.
            r"第(\d+(?:-\d+)?)條",  # 第1條 (中文)
        ]

        article_number = None
        clean_title = article_title.strip()

        for pattern in patterns:
            match = re.search(pattern, article_title, re.IGNORECASE)
            if match:
                article_number = match.group(1)
                break

        return article_number, clean_title

    def parse_constitution_html(self, soup, constitution_id):
        """
        解析憲法HTML內容
        :param soup: BeautifulSoup對象
        :param constitution_id: 憲法ID
        :return: 結構化的憲法數據
        """
        constitution_data = {
            "id": constitution_id,
            "title": "",
            "preamble": "",
            "chapters": [],
            "articles": [],
            "articles_index": {},  # 添加條文索引
            "full_text": "",
        }

        # 標題
        title_elem = soup.find("title")
        if title_elem:
            constitution_data["title"] = title_elem.get_text().strip()

        # 章節與條文
        sections = soup.find_all("div", class_="section")

        current_chapter = None
        current_chapter_number = 0

        for section in sections:
            section_id = section.get("id", "")

            # 章節標題
            chapter_header = section.find("h3", class_="depth-0")
            if chapter_header:
                chapter_title = chapter_header.get_text().strip()
                current_chapter_number += 1

                chapter_number_match = re.search(
                    r"Chapter\s+([IVXLCDM]+|\d+)", chapter_title, re.IGNORECASE
                )
                chapter_number = None
                if chapter_number_match:
                    chapter_number = chapter_number_match.group(1)

                current_chapter = {
                    "number": chapter_number,
                    "title": chapter_title,
                    "articles": [],
                    "order": current_chapter_number,
                }
                constitution_data["chapters"].append(current_chapter)
                continue

            # 條文
            article_header = section.find("h3", class_="depth-1")
            if article_header:
                article_title = article_header.get_text().strip()

                # 正規化條文編號
                article_number, clean_title = self.normalize_article_number(
                    article_title
                )

                # 內容
                article_content = []
                content_divs = section.find_all("div", class_="article-body")

                for content_div in content_divs:
                    # 段落
                    paragraphs = content_div.find_all("p", class_="content")
                    for p in paragraphs:
                        paragraph_text = p.get_text().strip()
                        if paragraph_text:
                            article_content.append(paragraph_text)

                    # 列表
                    lists = content_div.find_all("ol")
                    for ol in lists:
                        list_items = ol.find_all("li")
                        for i, li in enumerate(list_items, 1):
                            list_text = li.get_text().strip()
                            if list_text:
                                article_content.append(f"{i}. {list_text}")

                content_text = "\n".join(article_content)

                article_data = {
                    "number": article_number,
                    "title": clean_title,
                    "content": article_content,
                    "content_text": content_text,
                    "section_id": section_id,
                    "chapter": current_chapter["title"] if current_chapter else None,
                    "chapter_number": (
                        current_chapter["number"] if current_chapter else None
                    ),
                }

                constitution_data["articles"].append(article_data)

                # 索引
                if article_number:
                    constitution_data["articles_index"][article_number] = article_data

                if current_chapter:
                    current_chapter["articles"].append(article_data)

        # 前言（常見 id='s1'）
        preamble_section = soup.find("div", id="s1")
        if preamble_section:
            preamble_content = []
            content_divs = preamble_section.find_all("div", class_="article-body")
            for div in content_divs:
                paragraphs = div.find_all("p", class_="content")
                for p in paragraphs:
                    preamble_text = p.get_text().strip()
                    if preamble_text:
                        preamble_content.append(preamble_text)
            constitution_data["preamble"] = "\n".join(preamble_content)

        # 完整文本
        constitution_data["full_text"] = self.generate_full_text(constitution_data)

        return constitution_data

    def generate_full_text(self, constitution_data):
        """
        生成完整的憲法文本
        :param constitution_data: 憲法數據
        :return: 完整文本字符串
        """
        full_text_parts = []

        # 標題
        if constitution_data.get("title"):
            full_text_parts.append(constitution_data["title"])
            full_text_parts.append("=" * len(constitution_data["title"]))
            full_text_parts.append("")

        # 前言
        if constitution_data.get("preamble"):
            full_text_parts.append("PREAMBLE")
            full_text_parts.append("-" * 20)
            full_text_parts.append(constitution_data["preamble"])
            full_text_parts.append("")

        # 章節與條文
        for chapter in constitution_data.get("chapters", []):
            full_text_parts.append(chapter["title"])
            full_text_parts.append("-" * len(chapter["title"]))
            full_text_parts.append("")

            for article in chapter.get("articles", []):
                full_text_parts.append(article["title"])
                full_text_parts.append("")
                full_text_parts.append(article["content_text"])
                full_text_parts.append("")

        return "\n".join(full_text_parts)

    # ------------------ 條文查詢工具 ------------------
    def get_article_by_number(self, constitution_data, article_number):
        """
        根據條文編號獲取特定條文
        """
        article_number = str(article_number).strip()

        if article_number in constitution_data.get("articles_index", {}):
            return constitution_data["articles_index"][article_number]

        for stored_number, article in constitution_data.get(
            "articles_index", {}
        ).items():
            if stored_number == article_number or stored_number.endswith(
                f"-{article_number}"
            ):
                return article

        return None

    def get_articles_range(self, constitution_data, start_article, end_article):
        """
        獲取條文範圍
        """
        articles_in_range = []

        try:
            start_num = int(start_article)
            end_num = int(end_article)

            for article in constitution_data.get("articles", []):
                if article.get("number"):
                    try:
                        article_num = int(article["number"].split("-")[0])
                        if start_num <= article_num <= end_num:
                            articles_in_range.append(article)
                    except (ValueError, AttributeError):
                        continue

            articles_in_range.sort(
                key=lambda x: int(x["number"].split("-")[0]) if x.get("number") else 0
            )

        except ValueError:
            pass

        return articles_in_range

    def search_articles_by_keyword(self, constitution_data, keyword):
        """
        根據關鍵字搜索條文
        """
        matching_articles = []
        keyword_lower = keyword.lower()

        for article in constitution_data.get("articles", []):
            if keyword_lower in (article.get("title", "").lower()):
                matching_articles.append(article)
                continue

            content_text = article.get("content_text", "")
            if keyword_lower in content_text.lower():
                matching_articles.append(article)

        return matching_articles

    # ------------------ 檔案輸出 ------------------
    def save_to_json(self, data, filename):
        """
        保存數据到JSON文件（含 log）
        """
        try:
            safe = self.sanitize_filename(filename)
            payload = json.dumps(data, ensure_ascii=False, indent=2)
            with open(safe, "w", encoding="utf-8") as f:
                f.write(payload)
            self._make_logger().info(
                "write_json ok path=%s bytes=%d", safe, len(payload.encode("utf-8"))
            )
        except Exception as e:
            self._make_logger().exception("write_json failed path=%s: %s", filename, e)

    def save_to_csv(self, constitutions_data, filename):
        """
        保存憲法列表到CSV文件
        """
        try:
            safe = self.sanitize_filename(filename)
            with open(safe, "w", newline="", encoding="utf-8") as f:
                if not constitutions_data:
                    return

                fieldnames = constitutions_data[0].keys()
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(constitutions_data)

            self._make_logger().info(
                "write_csv ok path=%s rows=%d", safe, len(constitutions_data)
            )
        except Exception as e:
            self._make_logger().exception("write_csv failed path=%s: %s", filename, e)

    # ------------------ 批次爬取 ------------------
    def scrape_all_constitutions(self, limit=None, save_individual=True):
        """
        爬取所有憲法
        :param limit: 限制爬取數量，None為全部
        :param save_individual: 是否保存個別憲法文件
        :return: 所有憲法數據
        """
        constitutions_list = self.get_constitutions_list()

        if not constitutions_list:
            self.logger.error("無法獲取憲法列表")
            return []

        os.makedirs("constitutions_data", exist_ok=True)

        if limit:
            constitutions_list = constitutions_list[:limit]

        all_constitutions_data = []

        for i, constitution in enumerate(constitutions_list):
            constitution_id = constitution.get("id")
            country = constitution.get("country", "Unknown")

            self.logger.info(
                f"正在爬取 ({i+1}/{len(constitutions_list)}): {country} ({constitution_id})"
            )

            constitution_content = self.scrape_constitution_content(constitution_id)

            if constitution_content:
                full_constitution_data = {**constitution, **constitution_content}
                all_constitutions_data.append(full_constitution_data)

                if save_individual:
                    safe_id = self.sanitize_filename(constitution_id)
                    individual_filename = f"constitutions_data/{safe_id}.json"
                    self.save_to_json(full_constitution_data, individual_filename)

                # 純文本
                safe_id = self.sanitize_filename(constitution_id)
                text_filename = f"constitutions_data/{safe_id}.txt"
                try:
                    with open(text_filename, "w", encoding="utf-8") as f:
                        f.write(f"Constitution of {country}\n")
                        f.write("=" * 50 + "\n\n")
                        f.write(constitution_content.get("full_text", ""))
                    self._make_logger().info("write_text ok path=%s", text_filename)
                except Exception as e:
                    self._make_logger().exception(
                        "write_text failed path=%s: %s", text_filename, e
                    )

            if i < len(constitutions_list) - 1:
                time.sleep(self.delay)

        self.save_to_json(
            all_constitutions_data, "constitutions_data/all_constitutions.json"
        )

        basic_info = []
        for const in all_constitutions_data:
            basic_info.append(
                {
                    "id": const.get("id"),
                    "country": const.get("country"),
                    "title": const.get("title_long"),
                    "year_enacted": const.get("year_enacted"),
                    "in_force": const.get("in_force"),
                    "word_length": const.get("word_length"),
                    "region": const.get("region"),
                }
            )

        self.save_to_csv(basic_info, "constitutions_data/constitutions_list.csv")

        self.logger.info(f"爬取完成！共處理 {len(all_constitutions_data)} 部憲法")
        return all_constitutions_data

    # ------------------ Topics 搜尋 API ------------------
    def topic_constitutions(
        self,
        key: str,
        in_force: bool = True,
        is_draft: bool = False,
        ownership: str = "all",
        lang: str = "en",
    ) -> list[dict]:
        """
        依 Topic key 搜尋有哪些國家/文本命中（constopicsearch）
        回傳每筆含 id, country, title_long, in_force, year_enacted...（依官方回傳）
        """
        params = {
            "q": key,  # ← 由 key 改成 q
            "in_force": str(bool(in_force)).lower(),
            "is_draft": str(bool(is_draft)).lower(),
            "ownership": ownership,
            "lang": lang,
        }
        data = self._request_json("/service/constopicsearch", params=params)
        if isinstance(data, list):
            self._make_logger().info(
                "topic_constitutions key=%s -> %d hits", key, len(data)
            )
            return data
        self._make_logger().warning(
            "topic_constitutions key=%s -> unexpected payload type: %s",
            key,
            type(data).__name__ if data is not None else None,
        )
        return []

    def topic_sections(
        self,
        key: str,
        cons_id: str,
        in_force: bool = True,
        is_draft: bool = False,
        ownership: str = "all",
        lang: str = "en",
    ) -> list[dict]:
        """
        取得某一部憲法在該 Topic 下的相關片段（sectionstopicsearch）
        若 textsearch 失敗（如 500），自動 fallback 用 textsearch API。
        """
        params = {
            "q": key,
            "cons_id": cons_id.split("?")[0],
            "in_force": str(bool(in_force)).lower(),
            "is_draft": str(bool(is_draft)).lower(),
            "ownership": ownership,
            "lang": lang,
        }
        data = self._request_json("/service/textsearch", params=params)
        results = []
        key_id = cons_id.split("?")[0]
        # textsearch 正常回傳
        if isinstance(data, dict) and key_id in data:
            payload = data[key_id]
            html_list = payload.get("results") or []
            self._make_logger().info(
                "topic_sections key=%s cons_id=%s -> %d fragment(s)",
                key,
                key_id,
                len(html_list),
            )
            for html in html_list:
                parsed = self._parse_topic_section_fragment(html, key_id)
                self._make_logger().debug("fragment parsed -> %d item(s)", len(parsed))
                results.extend(parsed)
            if results:
                return results
        # textsearch 失敗或無片段，fallback 用 textsearch
        self._make_logger().warning(
            "topic_sections key=%s cons_id=%s -> fallback to textsearch", key, key_id
        )
        # fallback 也要用 "q" 參數
        textsearch_params = {
            "q": key,
            "cons_id": cons_id.split("?")[0],
            "in_force": str(bool(in_force)).lower(),
            "is_draft": str(bool(is_draft)).lower(),
            "ownership": ownership,
            "lang": lang,
        }
        textsearch_data = self._request_json(
            "/service/textsearch", params=textsearch_params
        )
        if isinstance(textsearch_data, dict) and "results" in textsearch_data:
            results = self._parse_textsearch_results(textsearch_data["results"], key_id)
            self._make_logger().info(
                "textsearch fallback key=%s cons_id=%s -> %d fragment(s)",
                key,
                key_id,
                len(results),
            )
            return results
        self._make_logger().warning(
            "textsearch fallback key=%s cons_id=%s -> no results", key, key_id
        )
        return []

    def _parse_topic_section_fragment(
        self, html_fragment: str, cons_id: str
    ) -> list[dict]:
        """
        解析 textsearch 回傳的單一 HTML 片段
        """
        soup = BeautifulSoup(html_fragment, "html.parser")

        header_link = soup.select_one("h4.article-header a.article-header__link")
        href = (
            urljoin(self.base_url, header_link["href"])
            if (header_link and header_link.has_attr("href"))
            else None
        )
        breadcrumb = (
            " > ".join(
                span.get_text(strip=True)
                for span in soup.select("span.article-breadcrumb")
                if span.get_text(strip=True)
            )
            or None
        )

        lead_node = soup.select_one("p.content")
        lead = lead_node.get_text(strip=True) if lead_node else None

        items = []
        for div in soup.select("div._result-list"):
            txt = div.get_text(" ", strip=True)
            if txt:
                items.append(txt)

        self._make_logger().debug(
            "parse_fragment cons_id=%s lead=%r items=%d href=%s",
            cons_id,
            lead,
            len(items),
            href,
        )
        return [
            {
                "cons_id": cons_id,
                "href": href,
                "breadcrumb": breadcrumb,
                "lead": lead,
                "items": items,
                "raw_html": html_fragment,
            }
        ]

    def _parse_textsearch_results(self, results_json, cons_id: str) -> list[dict]:
        """
        解析 textsearch API 回傳的 results，結構化為片段列表。
        """
        fragments = []
        for item in results_json:
            # 主要欄位：breadcrumb, lead, content, href
            breadcrumb = (
                " > ".join(item.get("breadcrumb", []))
                if item.get("breadcrumb")
                else None
            )
            lead = item.get("lead", None)
            content = item.get("content", None)
            href = (
                urljoin(self.base_url, item.get("href")) if item.get("href") else None
            )
            fragments.append(
                {
                    "cons_id": cons_id,
                    "href": href,
                    "breadcrumb": breadcrumb,
                    "lead": lead,
                    "items": [content] if content else [],
                    "raw_json": item,
                }
            )
        return fragments
