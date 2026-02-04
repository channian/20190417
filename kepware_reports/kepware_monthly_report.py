#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kepware Tag 月報生成器
用途：從 DuckDB 讀取 Kepware tag 資料，生成 Excel 月報
適合匯入 Power BI 進行視覺化
"""

import duckdb
import pandas as pd
from datetime import datetime
import json
import os
from pathlib import Path


class KepwareMonthlyReport:
    """Kepware Tag 月報生成類別"""

    def __init__(self, config_path='config.json'):
        """
        初始化報表生成器

        Args:
            config_path: 設定檔路徑
        """
        # 讀取設定檔
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)

        # 連接資料庫
        db_path = self.config['database']['path']
        print(f"正在連接資料庫: {db_path}")
        self.con = duckdb.connect(db_path, read_only=True)

        # 設定輸出資料夾
        self.output_dir = Path(self.config['report']['output_dir'])
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 報表日期
        self.report_date = datetime.now()

    def get_overview_stats(self):
        """取得總覽統計數據"""
        print("正在統計總覽數據...")

        # Tag 總數
        total_tags = self.con.execute("SELECT COUNT(*) FROM tags").fetchone()[0]

        # 本月新增 (created_date 在本月的)
        monthly_new = self.con.execute("""
            SELECT COUNT(*)
            FROM tags
            WHERE DATE_TRUNC('month', created_date) = DATE_TRUNC('month', CURRENT_DATE)
        """).fetchone()[0]

        # 專案總數
        total_projects = self.con.execute("SELECT COUNT(*) FROM projects").fetchone()[0]

        # 使用部門數 (去除 NULL)
        total_departments = self.con.execute("""
            SELECT COUNT(DISTINCT department)
            FROM tags
            WHERE department IS NOT NULL AND department != ''
        """).fetchone()[0]

        # 使用廠區數
        total_sites = self.con.execute("""
            SELECT COUNT(DISTINCT site)
            FROM tags
            WHERE site IS NOT NULL AND site != ''
        """).fetchone()[0]

        # 資料完成度統計
        total_records = total_tags
        fields_to_check = ['description', 'zone', 'bu', 'site', 'floor', 'owner', 'department']
        completeness = {}

        for field in fields_to_check:
            filled = self.con.execute(f"""
                SELECT COUNT(*)
                FROM tags
                WHERE {field} IS NOT NULL AND {field} != ''
            """).fetchone()[0]
            completeness[field] = round(filled / total_records * 100, 1) if total_records > 0 else 0

        return {
            'tag總數': total_tags,
            '本月新增': monthly_new,
            '專案總數': total_projects,
            '使用部門數': total_departments,
            '使用廠區數': total_sites,
            '資料完成度': completeness
        }

    def get_site_distribution(self):
        """取得各廠區的 Tag 分布"""
        print("正在統計廠區分布...")

        query = """
            SELECT
                COALESCE(site, '未分類') as 廠區,
                COUNT(*) as Tag數量,
                COUNT(DISTINCT department) as 部門數,
                COUNT(DISTINCT owner) as 負責人數
            FROM tags
            GROUP BY site
            ORDER BY COUNT(*) DESC
        """

        df = self.con.execute(query).df()
        return df

    def get_department_distribution(self):
        """取得各部門的 Tag 分布"""
        print("正在統計部門分布...")

        query = """
            SELECT
                COALESCE(department, '未分類') as 部門,
                COALESCE(site, '未分類') as 廠區,
                COUNT(*) as Tag數量
            FROM tags
            GROUP BY department, site
            ORDER BY COUNT(*) DESC
        """

        df = self.con.execute(query).df()
        return df

    def get_driver_distribution(self):
        """取得各 Driver 類型分布"""
        print("正在統計 Driver 分布...")

        query = """
            SELECT
                COALESCE(driver_type, '未分類') as Driver類型,
                COUNT(*) as Tag數量,
                ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as 百分比
            FROM tags
            GROUP BY driver_type
            ORDER BY COUNT(*) DESC
        """

        df = self.con.execute(query).df()
        return df

    def get_data_type_distribution(self):
        """取得各資料類型分布"""
        print("正在統計資料類型分布...")

        query = """
            SELECT
                COALESCE(data_type, '未分類') as 資料類型,
                COUNT(*) as Tag數量,
                ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as 百分比
            FROM tags
            GROUP BY data_type
            ORDER BY COUNT(*) DESC
        """

        df = self.con.execute(query).df()
        return df

    def get_project_stats(self):
        """取得專案統計"""
        print("正在統計專案資訊...")

        query = """
            SELECT
                p.project_name as 專案名稱,
                COUNT(tp.tag_id) as Tag數量,
                MIN(tp.date) as 最早加入日期,
                MAX(tp.date) as 最近加入日期
            FROM projects p
            LEFT JOIN tag_projects tp ON p.project_id = tp.project_id
            GROUP BY p.project_name
            ORDER BY COUNT(tp.tag_id) DESC
        """

        df = self.con.execute(query).df()
        return df

    def get_owner_stats(self):
        """取得負責人統計"""
        print("正在統計負責人資訊...")

        query = """
            SELECT
                COALESCE(owner, '未分類') as 負責人,
                COALESCE(department, '未分類') as 部門,
                COUNT(*) as Tag數量
            FROM tags
            GROUP BY owner, department
            ORDER BY COUNT(*) DESC
        """

        df = self.con.execute(query).df()
        return df

    def get_monthly_trend(self):
        """取得每月新增趨勢（如果有歷史資料）"""
        print("正在統計新增趨勢...")

        query = """
            SELECT
                DATE_TRUNC('month', created_date) as 月份,
                COUNT(*) as 新增數量
            FROM tags
            WHERE created_date IS NOT NULL
            GROUP BY DATE_TRUNC('month', created_date)
            ORDER BY 月份 DESC
            LIMIT 12
        """

        df = self.con.execute(query).df()
        return df

    def generate_report(self):
        """生成完整報表"""
        print("\n=== 開始生成 Kepware Tag 月報 ===\n")

        # 取得所有統計數據
        overview = self.get_overview_stats()
        site_dist = self.get_site_distribution()
        dept_dist = self.get_department_distribution()
        driver_dist = self.get_driver_distribution()
        datatype_dist = self.get_data_type_distribution()
        project_stats = self.get_project_stats()
        owner_stats = self.get_owner_stats()
        monthly_trend = self.get_monthly_trend()

        # 建立總覽 DataFrame
        overview_data = {
            '項目': [
                'Tag 總數',
                '本月新增',
                '專案總數',
                '使用部門數',
                '使用廠區數'
            ],
            '數值': [
                overview['tag總數'],
                overview['本月新增'],
                overview['專案總數'],
                overview['使用部門數'],
                overview['使用廠區數']
            ]
        }
        overview_df = pd.DataFrame(overview_data)

        # 建立資料完成度 DataFrame
        completeness_data = {
            '欄位': list(overview['資料完成度'].keys()),
            '完成度(%)': list(overview['資料完成度'].values())
        }
        completeness_df = pd.DataFrame(completeness_data)

        # 產生檔案名稱
        filename = f"{self.config['report']['file_prefix']}_{self.report_date.strftime('%Y%m')}.xlsx"
        output_path = self.output_dir / filename

        print(f"\n正在寫入 Excel 檔案: {output_path}")

        # 寫入 Excel（使用 xlsxwriter 引擎以支援格式設定）
        with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
            # Sheet 1: 總覽
            overview_df.to_excel(writer, sheet_name='總覽', index=False, startrow=2)
            completeness_df.to_excel(writer, sheet_name='總覽', index=False, startrow=10)

            # 在總覽頁面加上標題
            workbook = writer.book
            worksheet = writer.sheets['總覽']

            # 標題格式
            title_format = workbook.add_format({
                'bold': True,
                'font_size': 14,
                'align': 'center',
                'valign': 'vcenter'
            })

            worksheet.merge_range('A1:B1',
                f'Kepware Tag 管理月報 - {self.report_date.strftime("%Y年%m月")}',
                title_format)

            # Sheet 2: 廠區分布
            site_dist.to_excel(writer, sheet_name='廠區分布', index=False)

            # Sheet 3: 部門分布
            dept_dist.to_excel(writer, sheet_name='部門分布', index=False)

            # Sheet 4: Driver 統計
            driver_dist.to_excel(writer, sheet_name='Driver統計', index=False)

            # Sheet 5: 資料類型統計
            datatype_dist.to_excel(writer, sheet_name='資料類型統計', index=False)

            # Sheet 6: 專案統計
            project_stats.to_excel(writer, sheet_name='專案統計', index=False)

            # Sheet 7: 負責人統計
            owner_stats.to_excel(writer, sheet_name='負責人統計', index=False)

            # Sheet 8: 新增趨勢
            monthly_trend.to_excel(writer, sheet_name='新增趨勢', index=False)

            # 自動調整欄寬
            for sheet_name in writer.sheets:
                worksheet = writer.sheets[sheet_name]
                for i, col in enumerate(writer.sheets[sheet_name].table.columns):
                    max_len = max(
                        writer.sheets[sheet_name].table[col].astype(str).map(len).max(),
                        len(col)
                    ) + 2
                    worksheet.set_column(i, i, min(max_len, 50))

        print(f"\n✅ 報表生成完成！")
        print(f"📁 檔案位置: {output_path.absolute()}")
        print(f"\n=== 報表摘要 ===")
        print(f"Tag 總數: {overview['tag總數']:,}")
        print(f"本月新增: {overview['本月新增']}")
        print(f"專案總數: {overview['專案總數']}")
        print(f"資料完成度: 平均 {sum(overview['資料完成度'].values())/len(overview['資料完成度']):.1f}%")

        return output_path

    def close(self):
        """關閉資料庫連接"""
        self.con.close()


def main():
    """主程式"""
    try:
        # 檢查設定檔是否存在
        if not os.path.exists('config.json'):
            print("❌ 找不到 config.json！")
            print("請先複製 config.json.example 為 config.json，並修改資料庫路徑。")
            return

        # 建立報表生成器
        report = KepwareMonthlyReport('config.json')

        # 生成報表
        output_path = report.generate_report()

        # 關閉連接
        report.close()

        print("\n✨ 完成！可以用 Excel 或 Power BI 開啟報表了。")

    except Exception as e:
        print(f"\n❌ 發生錯誤: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
