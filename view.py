import eel

import desktop
import pos_system


def main():
    desktop.start('html', 'index.html', (800, 750))


@eel.expose
def create_select(file_name):
    try:
        master_csv = pos_system.ItemMasterCsv(file_name)
        order = pos_system.Order(master_csv)
        eel.set_items(order.get_master_dict())
    except:
        pass


@eel.expose
def pay(item_code_list, payment, masterFileName):
    try:
        master_csv = pos_system.ItemMasterCsv(masterFileName)
        order = pos_system.Order(master_csv)
        for item_code in item_code_list:
            order.add_item_order(item_code)

        receipt_file_name = order.pay(int(payment))
        eel.pay_result(receipt_file_name)
    except Exception as e:
        print(e)


if __name__ == '__main__':
    main()
