import sqlite3
from datetime import datetime
from typing import Optional, List, Dict

class Database:
def **init**(self, db_path: str = “referral_bot.db”):
self.db_path = db_path
self._create_tables()

```
def _get_conn(self):
    conn = sqlite3.connect(self.db_path)
    conn.row_factory = sqlite3.Row
    return conn

def _create_tables(self):
    """Jadvallarni yaratish"""
    with self._get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id     INTEGER PRIMARY KEY,
                username    TEXT DEFAULT '',
                full_name   TEXT DEFAULT '',
                referrer_id INTEGER DEFAULT NULL,
                joined_at   TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (referrer_id) REFERENCES users(user_id)
            )
        """)
        conn.commit()

def register_user(
    self,
    user_id: int,
    username: str,
    full_name: str,
    referrer_id: Optional[int] = None
) -> bool:
    """
    Foydalanuvchini ro'yxatdan o'tkazish.
    Yangi foydalanuvchi bo'lsa True, aks holda False qaytaradi.
    """
    with self._get_conn() as conn:
        existing = conn.execute(
            "SELECT user_id FROM users WHERE user_id = ?", (user_id,)
        ).fetchone()

        if existing:
            # Foydalanuvchi mavjud - username/full_name ni yangilash
            conn.execute(
                "UPDATE users SET username = ?, full_name = ? WHERE user_id = ?",
                (username, full_name, user_id)
            )
            conn.commit()
            return False  # Eski foydalanuvchi

        # Referrer mavjudligini tekshirish
        if referrer_id:
            ref_exists = conn.execute(
                "SELECT user_id FROM users WHERE user_id = ?", (referrer_id,)
            ).fetchone()
            if not ref_exists:
                referrer_id = None

        conn.execute(
            "INSERT INTO users (user_id, username, full_name, referrer_id, joined_at) VALUES (?, ?, ?, ?, ?)",
            (user_id, username, full_name, referrer_id, datetime.now().isoformat())
        )
        conn.commit()
        return True  # Yangi foydalanuvchi

def get_user(self, user_id: int) -> Optional[Dict]:
    """Foydalanuvchi ma'lumotlarini olish"""
    with self._get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE user_id = ?", (user_id,)
        ).fetchone()
        return dict(row) if row else None

def get_referrals(self, user_id: int) -> List[Dict]:
    """Foydalanuvchi taklif qilgan odamlar ro'yxati"""
    with self._get_conn() as conn:
        rows = conn.execute(
            """
            SELECT user_id, username, full_name, joined_at
            FROM users
            WHERE referrer_id = ?
            ORDER BY joined_at DESC
            """,
            (user_id,)
        ).fetchall()
        return [dict(r) for r in rows]

def get_referral_count(self, user_id: int) -> int:
    """Foydalanuvchi qo'shgan odamlar soni"""
    with self._get_conn() as conn:
        row = conn.execute(
            "SELECT COUNT(*) as cnt FROM users WHERE referrer_id = ?", (user_id,)
        ).fetchone()
        return row["cnt"] if row else 0

def get_top_referrers(self, limit: int = 10) -> List[Dict]:
    """Eng ko'p odam qo'shganlar reytingi"""
    with self._get_conn() as conn:
        rows = conn.execute(
            """
            SELECT
                u.user_id,
                u.username,
                u.full_name,
                COUNT(r.user_id) AS referral_count
            FROM users u
            LEFT JOIN users r ON r.referrer_id = u.user_id
            GROUP BY u.user_id
            HAVING referral_count > 0
            ORDER BY referral_count DESC
            LIMIT ?
            """,
            (limit,)
        ).fetchall()
        return [dict(r) for r in rows]

def get_total_users(self) -> int:
    """Jami foydalanuvchilar soni"""
    with self._get_conn() as conn:
        row = conn.execute("SELECT COUNT(*) as cnt FROM users").fetchone()
        return row["cnt"] if row else 0

def get_total_referrals(self) -> int:
    """Referral orqali qo'shilganlar soni"""
    with self._get_conn() as conn:
        row = conn.execute(
            "SELECT COUNT(*) as cnt FROM users WHERE referrer_id IS NOT NULL"
        ).fetchone()
        return row["cnt"] if row else 0
```