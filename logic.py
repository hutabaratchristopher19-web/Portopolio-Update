import sqlite3
from config import DATABASE


# =========================
# DATA DEFAULT
# =========================

skills = [
    ("Python",),
    ("SQL",),
    ("API",),
    ("Discord",)
]

statuses = [
    ("Prototipe",),
    ("Dalam Pengembangan",),
    ("Selesai",),
    ("Diperbarui",),
    ("Ditinggalkan/Tidak Dilanjutkan",)
]


# =========================
# DATABASE MANAGER
# =========================

class DB_Manager:

    def __init__(self, database):
        self.database = database

        # Pastikan database dan tabel tersedia
        self.create_tables()
        self.default_insert()

    # =========================
    # CREATE TABLES
    # =========================

    def create_tables(self):

        conn = sqlite3.connect(self.database)

        with conn:

            # Tabel status dibuat terlebih dahulu
            conn.execute("""
                CREATE TABLE IF NOT EXISTS status (
                    status_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    status_name TEXT NOT NULL UNIQUE
                )
            """)

            # Tabel skills
            conn.execute("""
                CREATE TABLE IF NOT EXISTS skills (
                    skill_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    skill_name TEXT NOT NULL UNIQUE
                )
            """)

            # Tabel projects
            conn.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    project_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    project_name TEXT NOT NULL,
                    description TEXT,
                    url TEXT,
                    status_id INTEGER,
                    FOREIGN KEY(status_id)
                        REFERENCES status(status_id)
                )
            """)

            # Tabel hubungan project dengan skill
            conn.execute("""
                CREATE TABLE IF NOT EXISTS project_skills (
                    project_id INTEGER,
                    skill_id INTEGER,

                    FOREIGN KEY(project_id)
                        REFERENCES projects(project_id),

                    FOREIGN KEY(skill_id)
                        REFERENCES skills(skill_id),

                    UNIQUE(project_id, skill_id)
                )
            """)

            conn.commit()

        print("Database siap digunakan.")

    # =========================
    # EXECUTEMANY
    # =========================

    def __executemany(self, sql, data):

        conn = sqlite3.connect(self.database)

        try:
            with conn:
                conn.executemany(sql, data)
                conn.commit()

        finally:
            conn.close()

    # =========================
    # SELECT
    # =========================

    def __select_data(self, sql, data=tuple()):

        conn = sqlite3.connect(self.database)

        try:
            cur = conn.cursor()
            cur.execute(sql, data)

            return cur.fetchall()

        finally:
            conn.close()

    # =========================
    # INSERT DEFAULT DATA
    # =========================

    def default_insert(self):

        # Insert skills
        sql = """
            INSERT OR IGNORE INTO skills (skill_name)
            VALUES (?)
        """

        self.__executemany(sql, skills)

        # Insert statuses
        sql = """
            INSERT OR IGNORE INTO status (status_name)
            VALUES (?)
        """

        self.__executemany(sql, statuses)

    # =========================
    # PROJECT
    # =========================

    def insert_project(self, data):

        sql = """
            INSERT INTO projects
            (
                user_id,
                project_name,
                url,
                status_id
            )
            VALUES (?, ?, ?, ?)
        """

        self.__executemany(sql, data)

    # =========================
    # SKILL
    # =========================

    def insert_skill(self, user_id, project_name, skill):

        project = self.__select_data(
            """
            SELECT project_id
            FROM projects
            WHERE project_name = ?
            AND user_id = ?
            """,
            (project_name, user_id)
        )

        if not project:
            return False

        project_id = project[0][0]

        skill_data = self.__select_data(
            """
            SELECT skill_id
            FROM skills
            WHERE skill_name = ?
            """,
            (skill,)
        )

        if not skill_data:
            return False

        skill_id = skill_data[0][0]

        data = [
            (project_id, skill_id)
        ]

        sql = """
            INSERT OR IGNORE INTO project_skills
            (
                project_id,
                skill_id
            )
            VALUES (?, ?)
        """

        self.__executemany(sql, data)

        return True

    # =========================
    # STATUS
    # =========================

    def get_statuses(self):

        sql = """
            SELECT status_name
            FROM status
            ORDER BY status_id
        """

        return self.__select_data(sql)

    # =========================
    # GET STATUS ID
    # =========================

    def get_status_id(self, status_name):

        sql = """
            SELECT status_id
            FROM status
            WHERE status_name = ?
        """

        result = self.__select_data(
            sql,
            (status_name,)
        )

        if result:
            return result[0][0]

        return None

    # =========================
    # GET PROJECTS
    # =========================

    def get_projects(self, user_id):

        sql = """
            SELECT *
            FROM projects
            WHERE user_id = ?
            ORDER BY project_id
        """

        return self.__select_data(
            sql,
            (user_id,)
        )

    # =========================
    # GET PROJECT ID
    # =========================

    def get_project_id(self, project_name, user_id):

        sql = """
            SELECT project_id
            FROM projects
            WHERE project_name = ?
            AND user_id = ?
        """

        result = self.__select_data(
            sql,
            (project_name, user_id)
        )

        if result:
            return result[0][0]

        return None

    # =========================
    # GET SKILLS
    # =========================

    def get_skills(self):

        sql = """
            SELECT *
            FROM skills
            ORDER BY skill_id
        """

        return self.__select_data(sql)

    # =========================
    # GET PROJECT SKILLS
    # =========================

    def get_project_skills(self, project_name):

        sql = """
            SELECT skill_name
            FROM projects
            JOIN project_skills
                ON projects.project_id = project_skills.project_id
            JOIN skills
                ON skills.skill_id = project_skills.skill_id
            WHERE project_name = ?
        """

        result = self.__select_data(
            sql,
            (project_name,)
        )

        return ", ".join(
            [x[0] for x in result]
        )

    # =========================
    # GET PROJECT INFO
    # =========================

    def get_project_info(self, user_id, project_name):

        sql = """
            SELECT
                project_name,
                description,
                url,
                status_name

            FROM projects

            JOIN status
                ON status.status_id = projects.status_id

            WHERE project_name = ?
            AND user_id = ?
        """

        return self.__select_data(
            sql,
            (project_name, user_id)
        )

    # =========================
    # UPDATE PROJECT
    # =========================

    def update_projects(self, param, data):

        allowed_columns = {
            "project_name",
            "description",
            "url",
            "status_id"
        }

        if param not in allowed_columns:
            return False

        sql = f"""
            UPDATE projects
            SET {param} = ?
            WHERE project_name = ?
            AND user_id = ?
        """

        self.__executemany(
            sql,
            [data]
        )

        return True

    # =========================
    # DELETE PROJECT
    # =========================

    def delete_project(self, user_id, project_id):

        sql = """
            DELETE FROM projects
            WHERE user_id = ?
            AND project_id = ?
        """

        self.__executemany(
            sql,
            [
                (user_id, project_id)
            ]
        )

    # =========================
    # DELETE SKILL
    # =========================

    def delete_skill(self, project_id, skill_id):

        sql = """
            DELETE FROM project_skills
            WHERE project_id = ?
            AND skill_id = ?
        """

        self.__executemany(
            sql,
            [
                (project_id, skill_id)
            ]
        )


# =========================
# TEST DATABASE
# =========================

if __name__ == "__main__":

    manager = DB_Manager(DATABASE)

    print("\n=== STATUS ===")

    print(manager.get_statuses())

    print("\n=== SKILLS ===")

    print(manager.get_skills())

    print("\nDatabase berhasil dibuat dan siap digunakan.")
