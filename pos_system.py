from datetime import datetime
import pandas as pd


# 区切り表示用の文字列
SEPARATOR = "=" * 20


def print_separator():
    print(SEPARATOR)


### 商品クラス
class Item:
    def __init__(self, item_code, item_name, price):
        self.item_code = item_code
        self.item_name = item_name

        # csvから読み込むため、明示的に型変換
        self.price = int(price)

    def get_price(self):
        return self.price

    def get_code(self):
        return self.item_code

    def to_dict(self):
        return {
            'code': self.item_code,
            'name': self.item_name,
            'price': self.price
        }

    def __str__(self) -> str:
        return f"(商品名：{self.item_name}, 価格：￥{self.price})"


### オーダークラス
class Order:
    def __init__(self, master_csv):
        self.item_order_list = []
        self.item_master = master_csv.read_rows()
        self.receipt = Receipt()

    def get_master_dict(self):
        return [item.to_dict() for item in self.item_master]

    def add_item_order(self, item_code):
        """
        オーダーの追加
        コードがマスタに存在すれば、そのマスタのインスタンスを返す
        存在しなければ、Noneを返す
        """
        for row in self.item_master:
            if row.get_code() == item_code:
                # 参照のコピーになるが、各商品独自の属性がないので問題なし
                self.item_order_list.append(row)
                return row
        return None

    def add_item_order_from_console(self):
        """
        コンソールからオーダーを登録する
        ユーザがすべて登録を終えるまで、繰り返す
        """
        # マスタに登録されている商品コード一覧
        code_list = [row.get_code() for row in self.item_master]

        # ユーザがキャンセルするまで繰り返し
        while True:
            print("===登録可能な商品コード===")
            print(f"[{', '.join(code_list)}]")

            item_code = input("商品コードを入力してください(終了:0)：")
            if item_code == "0":
                break

            count = input("個数を入力してください。")
            if not count.isdecimal() or count == "0":
                print("個数は１以上の整数で入力してください")
                continue

            for _ in range(int(count)):
                item = self.add_item_order(item_code)

            if item is not None:
                print(f"商品：{item}を{count}個 登録しました")
            else:
                print("その商品コードは存在しません")

    def sum_price(self):
        """
        登録されているオーダーの合計金額
        """
        return sum([item.get_price() for item in self.item_order_list])

    def view_item_list(self):
        """
        登録されているオーダーを表示
        """
        print_separator()
        for item in self.item_order_list:
            print(item)

        print(f"個数：{len(self.item_order_list)}")
        print(f"合計金額：{self.sum_price()}")

    def pay(self, payment):
        """
        支払処理
        """
        total = self.sum_price()

        if total > payment:
            return None

        # レシートへ金額を登録
        self.receipt.set_total_price(total)
        self.receipt.set_payment(payment)

        return self.write_receipt()

    def write_receipt(self):
        """
        レシート出力
        """
        self.receipt.set_item_list(self.item_order_list)
        return self.receipt.write()


### マスタのCSV（自作クラス）
class ItemMasterCsv:
    def __init__(self, path):
        self.path = path

    def read_rows(self):
        """
        読み込み処理
        """
        rows = []
        df = pd.read_csv(self.path)
        for row in df.itertuples():
            rows.append(Item(str(row.code).zfill(3), row.name, row.price))
        return rows


# レシート（自作クラス）
class Receipt:
    def __init__(self):
        self.item_list = []
        self.total_price = 0
        self.payment = 0

    def set_item_list(self, item_list):
        self.item_list = [f"{item}\n" for item in item_list]

    def set_total_price(self, total_price):
        self.total_price = total_price

    def set_payment(self, payment):
        self.payment = payment

    def write(self):
        """
        レシートの書き出し
        """
        now = datetime.now().strftime("%Y%m%d-%H%M%S")
        file_name = f"{now}.txt"
        with open(file_name, mode="w", encoding="utf-8") as f:
            f.write(f"日時：{now}\n")
            f.write(f"{SEPARATOR}\n")
            f.writelines(self.item_list)
            f.write(f"{SEPARATOR}\n")
            f.write(f"個数：{len(self.item_list)}個\n")
            f.write(f"合計金額：￥{self.total_price}\n")
            f.write(f"支払金額：￥{self.payment}\n")
            f.write(f"お釣り：￥{self.payment-self.total_price}\n")

        return file_name


### メイン処理
def main():
    # マスタ登録
    master_csv = ItemMasterCsv("master.csv")

    # オーダー登録
    order = Order(master_csv)

    order.add_item_order_from_console()

    # オーダー表示
    order.view_item_list()

    # 支払処理
    order.pay()

    # レシート出力
    order.write_receipt()

if __name__ == "__main__":
    main()
