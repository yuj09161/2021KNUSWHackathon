from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QApplication, QMainWindow,
    QGridLayout, QSizePolicy, QSpacerItem,
    QPushButton, QLineEdit, QComboBox,
    QWidget, QGroupBox,
    QTreeView, QLabel,
)

import os
import sqlite3


PROGRAM_DIR = os.path.abspath(os.path.dirname(__file__)) + '/'
USER_DB = PROGRAM_DIR + '../data/users.sqlite'


USER_TYPES = ('학부생', '대학원생', '교수')


sizePolicy_EP = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
sizePolicy_EP.setHorizontalStretch(0)
sizePolicy_EP.setVerticalStretch(0)


# Models
class BaseModel(QStandardItemModel):
    def __init__(self):
        super().__init__()
        self.set_header()

    # pylint: disable=dangerous-default-value
    def set_data(self, datas, additional_firsts=[], additional_lasts=[]):
        self.clear()
        if not (additional_firsts and additional_lasts):
            for data in datas:
                self.add_data(data)
        elif additional_firsts:
            assert isinstance(additional_firsts, list)
            assert len(datas) == len(additional_firsts)

            for data, additional_first in zip(datas, additional_firsts):
                self.add_data(data, additional_first)
        elif additional_lasts:
            assert isinstance(additional_lasts, list)
            assert len(datas) == len(additional_lasts)

            for data, additional_last in zip(datas, additional_lasts):
                self.add_data(data, additional_last)
        else:
            assert isinstance(additional_firsts, list)
            assert isinstance(additional_lasts, list)
            assert len(datas) == len(additional_firsts)\
                == len(additional_lasts)

            for data, additional_first, additional_last\
                    in zip(datas, additional_firsts, additional_lasts):
                self.add_data(data, additional_first, additional_last)
        self.set_header()

    def add_data(self, data, additional_first=None, additional_last=None):
        # caution: must syncronize with add_data method from CheckModel
        # Info: data must be iterable(list, tuple, zip etc.)
        items = []
        if additional_first:
            assert isinstance(additional_first, list)
            items += additional_first

        for d in data:
            item = QStandardItem(d)
            item.setEditable(False)
            items.append(item)

        if additional_last:
            assert isinstance(additional_last, list)
            items += additional_last

        self.appendRow(items)

    def clear(self):
        super().clear()
        self.set_header()

    def set_header(self):
        self.setHorizontalHeaderLabels(getattr(self, '_header', tuple()))


class CheckModel(BaseModel):
    def add_data(
        self, data, additional_first=None, additional_last=None,
        *, chk_enabled=True, chk_state=Qt.Checked
    ):  # pylint: disable=arguments-differ
        # caution: data must be iterable(list, tuple, zip etc.)
        if additional_first:
            assert isinstance(additional_first, list)
            items = [(QStandardItem(''), *others)
                     for others in additional_first]
            items[0].setEditable(False)
            items[0].setCheckable(True)
            items[0].setCheckState(chk_state if chk_enabled else Qt.Unchecked)
            items[0].setEnabled(chk_enabled)
        else:
            chk = QStandardItem('')
            chk.setEditable(False)
            chk.setCheckable(True)
            chk.setCheckState(chk_state if chk_enabled else Qt.Unchecked)
            chk.setEnabled(chk_enabled)
            items = [chk]

        # caution: must syncronize with add_data method from BaseModel
        for d in data:
            item = QStandardItem(d)
            item.setEditable(False)
            items.append(item)

        if additional_last:
            assert isinstance(additional_last, list)
            items += additional_last

        self.appendRow(items)

    @property
    def all_selected(self):
        for k in range(self.rowCount()):
            chk = self.item(k, 0)
            if chk.checkState() == Qt.Unchecked and chk.isEnabled():
                return False
        return True

    def is_selected(self):
        return [
            self.item(k, 0).checkState() == Qt.Checked
            for k in range(self.rowCount())
        ]

    def get_selected(self):
        return [
            k for k in range(self.rowCount())
            if self.item(k, 0).checkState() == Qt.Checked
        ]

    def del_selected(self):
        length = self.rowCount()
        k = 0
        deleted_row = []
        while k < length:
            if self.item(k, 0).checkState() == Qt.Checked:
                deleted_row.append(k)
                self.del_row(k)
                length -= 1
            else:
                k += 1
        return deleted_row

    def select_all(self):
        for k in range(self.rowCount()):
            chk = self.item(k, 0)
            if chk.isEnabled():
                chk.setCheckState(Qt.Checked)

    def clear_selection(self):
        for k in range(self.rowCount()):
            self.item(k, 0).setCheckState(Qt.Unchecked)

    def reverse_selection(self):
        for k in range(self.rowCount()):
            chk = self.item(k, 0)
            chk.setCheckState(
                Qt.Unchecked if chk.checkState() == Qt.Checked else Qt.Checked
            )

    def del_row(self, k):
        self.removeRow(k)


class UsersModel(CheckModel):
    _header = ('선택', '아이디', '비밀번호 (SHA256)', '구분', '닉네임')

    def __init__(self):
        super().__init__()
        self.__con = None
        self.__cur = None

        # load data
        self.__con = sqlite3.connect(USER_DB)
        self.__cur = self.__con.cursor()
        for username, password, usertype, nickname\
                in self.__cur.execute('SELECT * FROM users').fetchall():
            self.add_data(
                (username, password, USER_TYPES[usertype], nickname),
                chk_state=Qt.Unchecked
            )

    def add_user(self, username, password, usertype, nickname):
        self.__con.execute(
            'INSERT INTO users VALUES'
            f"('{username}', '{password}', {usertype}, '{nickname}')"
        )
        self.__con.commit()
        self.add_data(
            (username, password, USER_TYPES[usertype], nickname),
            chk_state=Qt.Unchecked
        )

    def del_selected_user(self):
        for k in self.get_selected():
            self.__con.execute(
                f"DELETE FROM users WHERE name='{self.item(k, 1).text()}'"
            )
        self.del_selected()
        self.__con.commit()
# end Model


# UIs
class Ui_MainWin:
    def setupUi(self, MainWin):
        # pylint: disable = redefined-outer-name
        # pylint: disable = attribute-defined-outside-init
        MainWin.resize(800, 600)

        self.centralWidget = QWidget(MainWin)
        self.glCent = QGridLayout(self.centralWidget)

        self.gbUsers = QGroupBox(self.centralWidget)
        self.glUsers = QGridLayout(self.gbUsers)

        self.tvUsers = QTreeView(self.gbUsers)
        self.glUsers.addWidget(self.tvUsers, 0, 0, 1, 4)

        self.btnSelect = QPushButton(self.gbUsers)
        self.glUsers.addWidget(self.btnSelect, 1, 0)

        self.btnReverse = QPushButton(self.gbUsers)
        self.glUsers.addWidget(self.btnReverse, 1, 1)

        self.glUsers.addItem(
            QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum),
            1, 2
        )

        self.btnSelDel = QPushButton(self.gbUsers)
        self.glUsers.addWidget(self.btnSelDel, 1, 3)

        self.glCent.addWidget(self.gbUsers, 0, 0)

        self.gbAddUser = QGroupBox(self.centralWidget)
        self.hlAddUser = QGridLayout(self.gbAddUser)

        self.lbUsername = QLabel(self.gbAddUser)
        self.lbUsername.setAlignment(Qt.AlignCenter)
        self.hlAddUser.addWidget(self.lbUsername, 0, 0)

        self.lnUsername = QLineEdit(self.gbAddUser)
        self.hlAddUser.addWidget(self.lnUsername, 0, 1)

        self.lbPassword = QLabel(self.gbAddUser)
        self.lbPassword.setAlignment(Qt.AlignCenter)
        self.hlAddUser.addWidget(self.lbPassword, 0, 2)

        self.lnPassword = QLineEdit(self.gbAddUser)
        self.hlAddUser.addWidget(self.lnPassword, 0, 3)

        self.lbUsertype = QLabel(self.gbAddUser)
        self.lbUsertype.setAlignment(Qt.AlignCenter)
        self.hlAddUser.addWidget(self.lbUsertype, 1, 0)

        self.comboUsertype = QComboBox(self.gbAddUser)
        sizePolicy_EP.setHeightForWidth(self.comboUsertype.hasHeightForWidth())
        self.comboUsertype.setSizePolicy(sizePolicy_EP)
        self.hlAddUser.addWidget(self.comboUsertype, 1, 1)

        self.lbNickname = QLabel(self.gbAddUser)
        self.lbNickname.setAlignment(Qt.AlignCenter)
        self.hlAddUser.addWidget(self.lbNickname, 1, 2)

        self.lnNickname = QLineEdit(self.gbAddUser)
        self.hlAddUser.addWidget(self.lnNickname, 1, 3)

        self.btnAddUser = QPushButton(self.gbAddUser)
        self.hlAddUser.addWidget(self.btnAddUser, 0, 4, 2, 1)

        self.glCent.addWidget(self.gbAddUser, 1, 0)

        MainWin.setCentralWidget(self.centralWidget)

        self.retranslateUi(MainWin)

    def retranslateUi(self, MainWin):
        # pylint: disable = redefined-outer-name
        MainWin.setWindowTitle('사용자 관리')

        self.gbUsers.setTitle('사용자 관리')
        self.btnSelect.setText('모두 선택')
        self.btnReverse.setText('선택 반전')
        self.btnSelDel.setText('선택 삭제')

        self.gbAddUser.setTitle('사용자 추가')
        self.lbUsername.setText('아이디')
        self.lbPassword.setText('암호 (SHA256)')
        self.lbUsertype.setText('사용자 구분')
        self.lbNickname.setText('별명')
        self.btnAddUser.setText('추가')
# end UI


class MainWin(QMainWindow, Ui_MainWin):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.__users = UsersModel()
        self.tvUsers.setModel(self.__users)
        self.comboUsertype.addItems(USER_TYPES)

        self.tvUsers.clicked.connect(self.__set_btnSelect_text)

        self.btnSelect.clicked.connect(self.__select)
        self.btnReverse.clicked.connect(self.__reverse_selection)
        self.btnSelDel.clicked.connect(self.__remove_selected)
        self.btnAddUser.clicked.connect(self.__add_user)

        self.__resize_columns()

    def __resize_columns(self):
        for k in range(self.__users.columnCount()):
            self.tvUsers.resizeColumnToContents(k)

    def __set_btnSelect_text(self, arg):
        if not isinstance(arg, bool):
            is_all_selected = arg.column() == 0 and self.__users.all_selected
        else:
            is_all_selected = arg
        self.btnSelect.setText('선택 해제' if is_all_selected else '모두 선택')

    def __select(self):
        if self.__users.all_selected:
            self.__users.clear_selection()
            self.__set_btnSelect_text(False)
        else:
            self.__users.select_all()
            self.__set_btnSelect_text(True)

    def __reverse_selection(self):
        self.__users.reverse_selection()
        self.__set_btnSelect_text(self.__users.all_selected)

    def __remove_selected(self):
        self.__users.del_selected_user()
        self.__resize_columns()

    def __add_user(self):
        self.__users.add_user(
            self.lnUsername.text(),
            self.lnPassword.text(),
            self.comboUsertype.currentIndex(),
            self.lnNickname.text()
        )

        self.lnUsername.clear()
        self.lnPassword.clear()
        self.comboUsertype.setCurrentIndex(0)
        self.lnNickname.clear()

        self.__resize_columns()


if __name__ == "__main__":
    app = QApplication()

    main = MainWin()
    main.show()

    app.exec()
