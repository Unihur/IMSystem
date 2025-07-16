import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
import mysql.connector
from mysql.connector import errorcode


class NorthwindManagementSystem:
    # 数据库连接信息
    DB_CONFIG = {
        'user': 'root',
        'password': '123456',
        'host': 'localhost',
        'database': 'northwind'
    }

    def __init__(self):
        self.connection = None
        self.connect_to_database()
        self.create_ui()

    # 连接数据库方法
    def connect_to_database(self):
        try:
            self.connection = mysql.connector.connect(**self.DB_CONFIG)
            print("数据库连接成功")
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                messagebox.showerror("错误", "数据库用户名或密码错误")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                messagebox.showerror("错误", "数据库不存在")
            else:
                messagebox.showerror("错误", f"数据库连接失败: {err}")
            exit(1)

    # 初始化用户界面
    def create_ui(self):
        self.root = tk.Tk()
        self.root.title("经贸公司信息管理系统")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)

        # 设置主窗口背景颜色
        self.root.configure(bg="#f0f0f0")

        # 创建主选项卡面板
        self.tab_control = ttk.Notebook(self.root)

        # 为每个表增加管理面板
        self.tab_control.add(self.create_table_panel("产品"), text="产品")
        self.tab_control.add(self.create_table_panel("订单"), text="订单")
        self.tab_control.add(self.create_table_panel("订单明细"), text="订单明细")
        self.tab_control.add(self.create_table_panel("供应商"), text="供应商")
        self.tab_control.add(self.create_table_panel("雇员"), text="雇员")
        self.tab_control.add(self.create_table_panel("客户"), text="客户")
        self.tab_control.add(self.create_table_panel("类别"), text="类别")
        self.tab_control.add(self.create_table_panel("运货商"), text="运货商")

        # 增加统计视图面板
        self.tab_control.add(self.create_statistics_panel(), text="统计")

        self.tab_control.pack(expand=1, fill='both', padx=10, pady=10)

        # 增加标题标签
        title_label = tk.Label(self.root, text="经贸公司信息管理系统", font=("Arial", 16, "bold"), bg="#f0f0f0")
        title_label.pack(pady=10)

        self.root.mainloop()

    # 创建表格管理面板
    def create_table_panel(self, table_name):
        frame = tk.Frame(self.root, bg="#f0f0f0")
        frame.pack(fill='both', expand=True)

        # 创建表格框架
        table_frame = tk.Frame(frame, bg="#f0f0f0")
        table_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # 创建表格
        self.table = ttk.Treeview(table_frame)
        self.table.pack(side='left', fill='both', expand=True)

        # 增加滚动条
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.table.yview)
        scrollbar.pack(side='right', fill='y')
        self.table.configure(yscrollcommand=scrollbar.set)

        # 加载表格数据
        self.load_table_data(table_name)

        # 创建按钮框架
        button_frame = tk.Frame(frame, bg="#f0f0f0")
        button_frame.pack(fill='x', padx=10, pady=10)

        # 创建按钮
        self.add_button = tk.Button(button_frame, text="增加", command=lambda: self.add_record(table_name), bg="#4CAF50", fg="white", font=("Arial", 10))
        self.delete_button = tk.Button(button_frame, text="删除", command=lambda: self.delete_record(table_name), bg="#F44336", fg="white", font=("Arial", 10))
        self.edit_button = tk.Button(button_frame, text="修改", command=lambda: self.edit_record(table_name), bg="#2196F3", fg="white", font=("Arial", 10))
        self.find_button = tk.Button(button_frame, text="查询", command=lambda: self.find_record(table_name), bg="#FFC107", fg="black", font=("Arial", 10))

        self.add_button.pack(side='right', padx=5, pady=5)
        self.delete_button.pack(side='right', padx=5, pady=5)
        self.edit_button.pack(side='right', padx=5, pady=5)
        self.find_button.pack(side='right', padx=5, pady=5)

        # 绑定表格选择事件
        self.table.bind('<<TreeviewSelect>>', lambda event: self.on_table_select())

        # 初始时禁用修改和删除按钮
        self.edit_button.config(state=tk.DISABLED)
        self.delete_button.config(state=tk.DISABLED)

        return frame

    # 加载表格数据
    def load_table_data(self, table_name):
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"SELECT * FROM {table_name}")
            columns = [column[0] for column in cursor.description]

            # 清空表格
            for item in self.table.get_children():
                self.table.delete(item)

            # 设置表头
            self.table['columns'] = columns
            self.table.heading('#0', text='ID')
            for col in columns:
                self.table.heading(col, text=col)
                self.table.column(col, width=100, anchor='center')  # 设置数据居中

            # 增加数据
            for row in cursor:
                self.table.insert('', 'end', values=row)

            cursor.close()
        except mysql.connector.Error as err:
            messagebox.showerror("错误", f"加载数据失败: {err}")

    # 增加记录
    def add_record(self, table_name):
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 0")
            columns = [column[0] for column in cursor.description]
            cursor.fetchall()
            cursor.close()

            # 创建输入对话框
            dialog = tk.Toplevel(self.root)
            dialog.title(f"增加{table_name}")
            dialog.resizable(False, False)
            dialog.configure(bg="#f0f0f0")

            input_entries = []
            for i, column in enumerate(columns):
                tk.Label(dialog, text=column, bg="#f0f0f0").grid(row=i, column=0, padx=5, pady=5)
                entry = tk.Entry(dialog)
                entry.grid(row=i, column=1, padx=5, pady=5)
                input_entries.append(entry)

            def save_record():
                try:
                    values = []
                    for entry in input_entries:
                        values.append(entry.get())

                    placeholders = ', '.join(['%s'] * len(columns))
                    query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"

                    cursor = self.connection.cursor()
                    cursor.execute(query, values)
                    self.connection.commit()
                    cursor.close()

                    messagebox.showinfo("成功", "记录增加成功")
                    dialog.destroy()
                    self.load_table_data(table_name)
                except mysql.connector.Error as err:
                    messagebox.showerror("错误", f"增加记录失败: {err}")

            tk.Button(dialog, text="保存", command=save_record, bg="#4CAF50", fg="white").grid(row=len(columns), column=0, padx=5, pady=10)
            tk.Button(dialog, text="取消", command=dialog.destroy, bg="#F44336", fg="white").grid(row=len(columns), column=1, padx=5, pady=10)

        except mysql.connector.Error as err:
            messagebox.showerror("错误", f"获取表结构失败: {err}")

    # 修改记录
    def edit_record(self, table_name):
        selected_item = self.table.selection()
        if not selected_item:
            messagebox.showinfo("提示", "请选择要修改的记录")
            return

        try:
            values = self.table.item(selected_item[0], 'values')
            cursor = self.connection.cursor()
            cursor.execute(f"SHOW COLUMNS FROM {table_name}")
            columns = [column[0] for column in cursor.fetchall()]
            cursor.close()

            # 创建输入对话框
            dialog = tk.Toplevel(self.root)
            dialog.title(f"修改{table_name}")
            dialog.resizable(False, False)
            dialog.configure(bg="#f0f0f0")

            input_entries = []
            for i, (column, value) in enumerate(zip(columns, values)):
                tk.Label(dialog, text=column, bg="#f0f0f0").grid(row=i, column=0, padx=5, pady=5)
                entry = tk.Entry(dialog)
                entry.insert(0, value)
                entry.grid(row=i, column=1, padx=5, pady=5)
                input_entries.append(entry)

            def update_record():
                try:
                    new_values = []
                    for entry in input_entries:
                        new_values.append(entry.get())

                    update_columns = [f"{col} = %s" for col in columns]
                    query = f"UPDATE {table_name} SET {', '.join(update_columns)} WHERE {columns[0]} = %s"

                    new_values.append(values[0])

                    cursor = self.connection.cursor()
                    cursor.execute(query, new_values)
                    self.connection.commit()
                    cursor.close()

                    messagebox.showinfo("成功", "记录修改成功")
                    dialog.destroy()
                    self.load_table_data(table_name)
                except mysql.connector.Error as err:
                    messagebox.showerror("错误", f"修改记录失败: {err}")

            tk.Button(dialog, text="保存", command=update_record, bg="#2196F3", fg="white").grid(row=len(columns), column=0, padx=5, pady=10)
            tk.Button(dialog, text="取消", command=dialog.destroy, bg="#F44336", fg="white").grid(row=len(columns), column=1, padx=5, pady=10)

        except mysql.connector.Error as err:
            messagebox.showerror("错误", f"修改记录失败: {err}")

    # 删除记录
    def delete_record(self, table_name):
        selected_item = self.table.selection()
        if not selected_item:
            messagebox.showinfo("提示", "请选择要删除的记录")
            return

        confirm = messagebox.askyesno("确认", "确定要删除选中的记录吗？")
        if not confirm:
            return

        try:
            value = self.table.item(selected_item[0], 'values')[0]

            cursor = self.connection.cursor()
            query = f"DELETE FROM {table_name} WHERE {table_name}ID = %s"
            cursor.execute(query, (value,))
            self.connection.commit()
            cursor.close()

            messagebox.showinfo("成功", "记录删除成功")
            self.load_table_data(table_name)
        except mysql.connector.Error as err:
            messagebox.showerror("错误", f"删除记录失败: {err}")

    # 查询记录
    def find_record(self, table_name):
        dialog = tk.Toplevel(self.root)
        dialog.title(f"查询{table_name}")
        dialog.resizable(False, False)
        dialog.configure(bg="#f0f0f0")

        tk.Label(dialog, text="请输入查询条件:", bg="#f0f0f0").grid(row=0, column=0, padx=5, pady=5)
        search_entry = tk.Entry(dialog)
        search_entry.grid(row=0, column=1, padx=5, pady=5)

        def search():
            keyword = search_entry.get()
            if not keyword:
                messagebox.showinfo("提示", "请输入查询条件")
                return

            try:
                cursor = self.connection.cursor()
                query = f"SELECT * FROM {table_name} WHERE "
                columns = []
                cursor.execute(f"SHOW COLUMNS FROM {table_name}")
                for column in cursor:
                    columns.append(column[0])
                query += " OR ".join([f"{col} LIKE '%{keyword}%'" for col in columns])

                cursor.execute(query)
                result = cursor.fetchall()
                cursor.close()

                if not result:
                    messagebox.showinfo("提示", "没有找到匹配的记录")
                    return

                # 显示查询结果
                result_dialog = tk.Toplevel(self.root)
                result_dialog.title(f"查询结果 - {table_name}")
                result_dialog.geometry("800x500")
                result_dialog.configure(bg="#f0f0f0")

                result_table = ttk.Treeview(result_dialog)
                result_table.pack(side='left', fill='both', expand=True)

                scrollbar = ttk.Scrollbar(result_dialog, orient='vertical', command=result_table.yview)
                scrollbar.pack(side='right', fill='y')
                result_table.configure(yscrollcommand=scrollbar.set)

                result_table['columns'] = columns
                result_table.heading('#0', text='ID')
                for col in columns:
                    result_table.heading(col, text=col)
                    result_table.column(col, width=100, anchor='center')  # 设置数据居中

                for row in result:
                    result_table.insert('', 'end', values=row)

            except mysql.connector.Error as err:
                messagebox.showerror("错误", f"查询记录失败: {err}")

        tk.Button(dialog, text="查询", command=search, bg="#2196F3", fg="white").grid(row=1, column=0, padx=5, pady=10)
        tk.Button(dialog, text="取消", command=dialog.destroy, bg="#F44336", fg="white").grid(row=1, column=1, padx=5, pady=10)

    # 创建统计分析面板
    def create_statistics_panel(self):
        frame = tk.Frame(self.root, bg="#f0f0f0")
        frame.pack(fill='both', expand=True)

        # 创建选项卡
        stats_tab_control = ttk.Notebook(frame)

        # 增加各种统计视图
        stats_tab_control.add(self.create_order_details_view_panel(), text="订单详情")
        stats_tab_control.add(self.create_product_sales_stats_panel(), text="产品销售统计")
        stats_tab_control.add(self.create_supplier_products_panel(), text="供应商产品")
        stats_tab_control.add(self.create_order_total_panel(), text="订单总金额")

        stats_tab_control.pack(expand=1, fill='both', padx=10, pady=10)

        return frame

    # 创建订单详情视图面板
    def create_order_details_view_panel(self):
        frame = tk.Frame(self.root, bg="#f0f0f0")
        frame.pack(fill='both', expand=True)

        # 创建表格框架
        table_frame = tk.Frame(frame, bg="#f0f0f0")
        table_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # 创建表格
        self.order_details_table = ttk.Treeview(table_frame)
        self.order_details_table.pack(side='left', fill='both', expand=True)

        # 增加滚动条
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.order_details_table.yview)
        scrollbar.pack(side='right', fill='y')
        self.order_details_table.configure(yscrollcommand=scrollbar.set)

        # 加载订单详情视图数据
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                CREATE OR REPLACE VIEW OrderDetailsView AS
                SELECT 
                    o.订单ID,
                    o.客户ID,
                    o.雇员ID,
                    o.订购日期,
                    od.产品ID,
                    od.数量,
                    od.单价,
                    od.折扣
                FROM 订单 o
                JOIN 订单明细 od ON o.订单ID = od.订单ID
            """)
            self.connection.commit()

            cursor.execute("SELECT * FROM OrderDetailsView")
            columns = [column[0] for column in cursor.description]

            # 设置表头
            self.order_details_table['columns'] = columns
            self.order_details_table.heading('#0', text='ID')
            for col in columns:
                self.order_details_table.heading(col, text=col)
                self.order_details_table.column(col, width=100, anchor='center')  # 设置数据居中

            # 增加数据
            for row in cursor:
                self.order_details_table.insert('', 'end', values=row)

            cursor.close()
        except mysql.connector.Error as err:
            messagebox.showerror("错误", f"加载数据失败: {err}")

        return frame

    # 创建产品销售统计面板
    def create_product_sales_stats_panel(self):
        frame = tk.Frame(self.root, bg="#f0f0f0")
        frame.pack(fill='both', expand=True)

        # 创建表格框架
        table_frame = tk.Frame(frame, bg="#f0f0f0")
        table_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # 创建表格
        self.sales_stats_table = ttk.Treeview(table_frame)
        self.sales_stats_table.pack(side='left', fill='both', expand=True)

        # 增加滚动条
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.sales_stats_table.yview)
        scrollbar.pack(side='right', fill='y')
        self.sales_stats_table.configure(yscrollcommand=scrollbar.set)

        # 加载产品销售统计数据
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                CREATE OR REPLACE VIEW ProductSalesStats AS
                SELECT 
                    p.产品ID,
                    p.产品名称,
                    p.供应商ID,
                    p.类别ID,
                    p.单价,
                    p.库存量,
                    SUM(od.数量) AS 销售数量,
                    SUM(od.数量 * od.单价 * (1 - od.折扣)) AS 销售金额
                FROM 产品 p
                JOIN 订单明细 od ON p.产品ID = od.产品ID
                GROUP BY p.产品ID
            """)
            self.connection.commit()

            cursor.execute("SELECT * FROM ProductSalesStats")
            columns = [column[0] for column in cursor.description]

            # 设置表头
            self.sales_stats_table['columns'] = columns
            self.sales_stats_table.heading('#0', text='ID')
            for col in columns:
                self.sales_stats_table.heading(col, text=col)
                self.sales_stats_table.column(col, width=100, anchor='center')  # 设置数据居中

            # 增加数据
            for row in cursor:
                self.sales_stats_table.insert('', 'end', values=row)

            cursor.close()
        except mysql.connector.Error as err:
            messagebox.showerror("错误", f"加载数据失败: {err}")

        return frame

    # 创建供应商产品面板
    def create_supplier_products_panel(self):
        frame = tk.Frame(self.root, bg="#f0f0f0")
        frame.pack(fill='both', expand=True)

        # 创建供应商选择下拉框
        top_panel = tk.Frame(frame, bg="#f0f0f0")
        top_panel.pack(fill='x', padx=10, pady=10)

        tk.Label(top_panel, text="选择供应商:", bg="#f0f0f0").pack(side='left', padx=5, pady=5)
        self.supplier_combo = ttk.Combobox(top_panel)
        self.supplier_combo.pack(side='left', padx=5, pady=5)

        # 填充供应商下拉框
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT 供应商ID, 公司名称 FROM 供应商")
            suppliers = [f"{row[0]} - {row[1]}" for row in cursor]
            self.supplier_combo['values'] = suppliers
            cursor.close()
        except mysql.connector.Error as err:
            messagebox.showerror("错误", f"加载供应商数据失败: {err}")

        load_button = tk.Button(top_panel, text="加载产品", command=self.load_supplier_products, bg="#2196F3", fg="white")
        load_button.pack(side='left', padx=5, pady=5)

        # 创建表格框架
        table_frame = tk.Frame(frame, bg="#f0f0f0")
        table_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # 创建表格
        self.supplier_products_table = ttk.Treeview(table_frame)
        self.supplier_products_table.pack(side='left', fill='both', expand=True)

        # 增加滚动条
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.supplier_products_table.yview)
        scrollbar.pack(side='right', fill='y')
        self.supplier_products_table.configure(yscrollcommand=scrollbar.set)

        return frame

    def load_supplier_products(self):
        try:
            supplier_id = self.supplier_combo.get().split()[0]
            if not supplier_id:
                messagebox.showinfo("提示", "请选择供应商")
                return

            cursor = self.connection.cursor()
            query = """
                SELECT p.产品ID, p.产品名称, p.单价, p.库存量
                FROM 产品 p
                WHERE p.供应商ID = %s
            """
            cursor.execute(query, (supplier_id,))

            columns = ['产品ID', '产品名称', '单价', '库存量']

            # 清空表格
            for item in self.supplier_products_table.get_children():
                self.supplier_products_table.delete(item)

            # 设置表头
            self.supplier_products_table['columns'] = columns
            self.supplier_products_table.heading('#0', text='ID')
            for col in columns:
                self.supplier_products_table.heading(col, text=col)
                self.supplier_products_table.column(col, width=100, anchor='center')  # 设置数据居中

            # 增加数据
            for row in cursor:
                self.supplier_products_table.insert('', 'end', values=row)

            cursor.close()
        except mysql.connector.Error as err:
            messagebox.showerror("错误", f"加载产品数据失败: {err}")

    # 创建订单总金额面板
    def create_order_total_panel(self):
        frame = tk.Frame(self.root, bg="#f0f0f0")
        frame.pack(fill='both', expand=True)

        # 创建订单选择下拉框
        top_panel = tk.Frame(frame, bg="#f0f0f0")
        top_panel.pack(fill='x', padx=10, pady=10)

        tk.Label(top_panel, text="选择订单:", bg="#f0f0f0").pack(side='left', padx=5, pady=5)
        self.order_combo = ttk.Combobox(top_panel)
        self.order_combo.pack(side='left', padx=5, pady=5)

        # 填充订单下拉框
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT 订单ID FROM 订单")
            orders = [str(row[0]) for row in cursor]
            self.order_combo['values'] = orders
            cursor.close()
        except mysql.connector.Error as err:
            messagebox.showerror("错误", f"加载订单数据失败: {err}")

        calculate_button = tk.Button(top_panel, text="计算总金额", command=self.calculate_order_total, bg="#2196F3", fg="white")
        calculate_button.pack(side='left', padx=5, pady=5)

        self.order_total_label = tk.Label(top_panel, text="订单总金额: ", bg="#f0f0f0")
        self.order_total_label.pack(side='left', padx=5, pady=5)

        return frame

    def calculate_order_total(self):
        try:
            order_id = self.order_combo.get()
            if not order_id:
                messagebox.showinfo("提示", "请选择订单")
                return

            cursor = self.connection.cursor()
            query = """
                SELECT SUM(数量 * 单价 * (1 - 折扣)) AS 总金额
                FROM 订单明细
                WHERE 订单ID = %s
            """
            cursor.execute(query, (order_id,))

            result = cursor.fetchone()
            cursor.close()

            if result and result[0]:
                self.order_total_label.config(text=f"订单总金额: {result[0]}")
            else:
                self.order_total_label.config(text="订单总金额: 0")

        except mysql.connector.Error as err:
            messagebox.showerror("错误", f"计算总金额失败: {err}")

    # 表格选择事件处理
    def on_table_select(self):
        selected_items = self.table.selection()
        if selected_items:
            self.edit_button.config(state=tk.NORMAL)
            self.delete_button.config(state=tk.NORMAL)
        else:
            self.edit_button.config(state=tk.DISABLED)
            self.delete_button.config(state=tk.DISABLED)


if __name__ == "__main__":
    app = NorthwindManagementSystem()