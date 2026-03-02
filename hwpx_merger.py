import sys
import zipfile
import shutil
import os
import tempfile
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QFileDialog, QListWidget, QMessageBox
)


class HWPXMerger(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HWPX 병합 프로그램")
        self.setGeometry(300, 300, 500, 400)

        self.layout = QVBoxLayout()

        self.file_list = QListWidget()
        self.layout.addWidget(self.file_list)

        self.add_button = QPushButton("HWPX 파일 추가")
        self.add_button.clicked.connect(self.add_files)
        self.layout.addWidget(self.add_button)

        self.merge_button = QPushButton("병합 후 저장")
        self.merge_button.clicked.connect(self.merge_files)
        self.layout.addWidget(self.merge_button)

        self.setLayout(self.layout)

    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "HWPX 파일 선택", "", "HWPX Files (*.hwpx)"
        )
        for file in files:
            self.file_list.addItem(file)

    def merge_files(self):
        if self.file_list.count() < 2:
            QMessageBox.warning(self, "경고", "2개 이상의 파일을 선택하세요.")
            return

        save_path, _ = QFileDialog.getSaveFileName(
            self, "저장 위치 선택", "", "HWPX Files (*.hwpx)"
        )

        if not save_path:
            return

        temp_dir = tempfile.mkdtemp()

        try:
            merged_xml = ""

            for i in range(self.file_list.count()):
                file_path = self.file_list.item(i).text()
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)

                section_path = os.path.join(temp_dir, "Contents", "section0.xml")
                if os.path.exists(section_path):
                    with open(section_path, "r", encoding="utf-8") as f:
                        xml_data = f.read()
                        merged_xml += xml_data

            # 첫 번째 파일을 템플릿으로 사용
            shutil.copy(self.file_list.item(0).text(), save_path)

            with zipfile.ZipFile(save_path, 'a') as zip_write:
                zip_write.writestr("Contents/section0.xml", merged_xml)

            QMessageBox.information(self, "완료", "병합 완료!")

        except Exception as e:
            QMessageBox.critical(self, "오류", str(e))

        finally:
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HWPXMerger()
    window.show()
    sys.exit(app.exec_())
