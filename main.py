import os
import glob

import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk, ExifTags

class ImageViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Viewer")
        #self.root.geometry("1300x1200")
        
        # tkinter process에서 공유 되는 string 변수
        self.selected_folder = tk.StringVar()
        self.selected_file = tk.StringVar()
        self.rating = tk.StringVar()
        
        # 왼쪽에 위치하는 프레임
        # 버튼과 리스트박스가 위치함
        self.left_side_frame = tk.Frame(self.root)

        # 왼쪽에 위치하는 프레임에 들어가는 요소들을 생성하는 함수
        self.create_widgets()
        
        # 키보드 이벤트를 바인딩하는 함수
        self.event_bind_key()

    def create_widgets(self):
        """왼쪽에 위치하는 프레임에 들어가는 요소들을 생성함
        """
        box_w = 3
        box_h = 1
        
        button_frame = tk.Frame(self.left_side_frame)        
        self.left_side_frame.pack(side=tk.LEFT,pady=10)
        button_frame.pack(pady=10)
        self.button = tk.Button(button_frame, text="Select Folder", command=self.select_folder,width=20, height=5)
        self.button.pack(padx=3, pady=3)
        text = tk.Label(button_frame, text="Grade Filter", font=("Helvetica", 16))
        text.pack()
        
        btn_5 = tk.Button(button_frame, text='5', command=None, width=box_w, height=box_h)
        btn_5.pack(side=tk.LEFT, padx=3, pady=3)
        btn_4 = tk.Button(button_frame, text='4', command=None, width=box_w, height=box_h)
        btn_4.pack(side=tk.LEFT, padx=3, pady=3)
        btn_3 = tk.Button(button_frame, text='3', command=None, width=box_w, height=box_h)
        btn_3.pack(side=tk.LEFT, padx=3, pady=3)
        btn_2 = tk.Button(button_frame, text='2', command=None, width=box_w, height=box_h)
        btn_2.pack(side=tk.LEFT, padx=3, pady=3)
        btn_1 = tk.Button(button_frame, text='1', command=None, width=box_w, height=box_h)
        btn_1.pack(side=tk.LEFT, padx=3, pady=3)
    
    def event_bind_key(self):
        self.root.bind("n", self.next_image)
        self.root.bind("b", self.before_image)
        self.root.bind("5", self._modify_exif_rating_to_five)
        self.root.bind("4", self._modify_exif_rating_to_four)
        self.root.bind("3", self._modify_exif_rating_to_three)
        self.root.bind("2", self._modify_exif_rating_to_two)
        self.root.bind("1", self._modify_exif_rating_to_one)
        
    def get_img_list(self, folder_path):
        jpg_file_list = glob.glob(folder_path + "/*.jpg")
        jpeg_file_list = glob.glob(folder_path + "/*.jpeg")
        png_file_list = glob.glob(folder_path + "/*.png")

        file_list = jpg_file_list + jpeg_file_list + png_file_list
        file_list.sort()
        file_name_list = [os.path.basename(file) for file in file_list]
        return file_name_list

    def select_folder(self):
        folder_path = filedialog.askdirectory()
        self.listbox = tk.Listbox(self.left_side_frame, selectmode=tk.SINGLE, width=20, height=30,font=("Helvetica", 16))
        self.listbox.pack(side=tk.LEFT, padx=30, pady=30)
        self.listbox.bind("<<ListboxSelect>>", self.select_img)
        if folder_path:
            self.selected_folder.set(folder_path)
            file_name_list = self.get_img_list(folder_path)
            for item in file_name_list:
                self.listbox.insert(tk.END, item)

    def select_img(self, event):
        widget = event.widget
        selection = widget.curselection()
        file_name = widget.get(selection[0])
        
        # 리스트박스에서 선택된 항목이 보이도록 스크롤을 이동시킴
        listbox_index = selection[0]
        self.listbox.see(listbox_index)
        
        # 선택된 이미지를 불러 올 수 있도록 경로를 생성 한뒤 OS에 맞게 정리 함
        file_path = os.path.join(self.selected_folder.get(), file_name)
        file_path = os.path.normpath(file_path)
        self.selected_file = file_path
        
        # 선택된 이미지를 불러옴
        img = Image.open(file_path)
        
        # 선택된 이미지의 등급을 불러옴
        self.show_exif_rating(file_path)
        
        # 선택된 이미지의 방향을 확인하여 회전시킴
        fixed_img = self._fix_orientation(img)
        
        # 이미지와 연결을 끊음
        img.close()
        
        # 이미지를 tkinter에서 사용할 수 있도록 변환
        photo_img = ImageTk.PhotoImage(fixed_img)
        
        # 이미지를 보여주기 위해 기존에 있던 요소들을 제거함
        for label in self.root.pack_slaves():
            label.pack_forget()
        
        # 등급을 보여주기 위해 기존에 있던 요소들을 제거함
        for rating_text in self.root.pack_slaves():
            rating_text.pack_forget()
        
        # 버튼 프레임을 생성함
        self.left_side_frame.pack(side=tk.LEFT,pady=10)
        
        # 이미지를 보여주기 위해 라벨을 생성함
        label = tk.Label(self.root, image=photo_img)
        label.image = photo_img
        label.pack(padx=20, pady=30)
        
        # 등급을 보여주기 위해 라벨을 생성함
        rating_text = tk.Label(self.root, text=f"Rating:{self.rating}", font=("Helvetica", 16))
        rating_text.pack(padx=20, pady=30)
        
        
    def _modify_exif_rating_to_five(self,event):
        rating=5
        self._modify_exif_rating(self.selected_file, rating)
        self.listbox.event_generate("<<ListboxSelect>>")
    
    def _modify_exif_rating_to_four(self,event):
        rating=4
        self._modify_exif_rating(self.selected_file, rating)
        self.listbox.event_generate("<<ListboxSelect>>")
    
    def _modify_exif_rating_to_three(self,event):
        rating=3
        self._modify_exif_rating(self.selected_file, rating)
        self.listbox.event_generate("<<ListboxSelect>>")
    
    def _modify_exif_rating_to_two(self,event):
        rating=2
        self._modify_exif_rating(self.selected_file, rating)
        self.listbox.event_generate("<<ListboxSelect>>")
    
    def _modify_exif_rating_to_one(self,event):
        rating=1
        self._modify_exif_rating(self.selected_file, rating)
        self.listbox.event_generate("<<ListboxSelect>>")
    
    def _modify_exif_rating(self,image_path, rating):
        try:
            img = Image.open(image_path)
            exif_data = img.getexif()
            
            # exif 데이터에 등급 정보 추가 (태그 번호: 18246, 태그 이름: Rating)
            exif_data.update({18246:rating})
            
            # 이미지에 변경된 exif 데이터 적용
            img.save(image_path, exif=exif_data)
            
            print(f"{image_path}\' rank is changed to {rating}.")
        except Exception as e:
            print(f"Error is Occur: {e}")
    
    def show_exif_rating(self,file_path):
        try:
            img = Image.open(file_path)
            exif_data = img._getexif()
            rating = exif_data.get(18246, None)
            self.rating = rating
            img.close()
        except Exception as e:
                print(f"Error is Occur in show_exif_rating: {e}")

    def _fix_orientation(self, img):
        # 이미지의 EXIF 데이터를 해석하여 회전 정보를 확인하고 올바른 방향으로 회전시킴
        exif_orientation_tag = 0x0112  # EXIF orientation tag
        if hasattr(img, '_getexif'):  # only present in JPEGs
            exif = img._getexif()       # returns None if no EXIF data
            if exif is not None:
                orientation = exif.get(exif_orientation_tag, 1)
                # 1: 0 degrees, 3: 180 degrees, 6: 270 degrees, 8: 90 degrees
                if orientation == 3:
                    img = img.rotate(180, expand=True)
                    img = img.resize((1500,843))
                elif orientation == 6:
                    img = img.rotate(270, expand=True)
                    img = img.resize((520,924))
                elif orientation == 8:
                    img = img.rotate(90, expand=True)
                    img = img.resize((520,924))
                else:
                    img = img.resize((1500,843))
        return img


    def next_image(self, event):
        # Get the current selection in the listbox
        current_selection = self.listbox.curselection()

        # If there is no selection or the last image is selected, do nothing
        if not current_selection or current_selection[0] == self.listbox.size() - 1:
            return

        # Deselect the current image
        self.listbox.selection_clear(current_selection[0])

        # Select the next image in the listbox
        next_index = current_selection[0] + 1
        self.listbox.selection_set(next_index)
        
        # Listbox를 선택하는 이벤트를 발생시켜서 선택된 이미지를 보여줌
        self.listbox.event_generate("<<ListboxSelect>>")
        
    
    def before_image(self, event):
        # Get the current selection in the listbox
        current_selection = self.listbox.curselection()

        # If there is no selection or the last image is selected, do nothing
        if not current_selection or current_selection[0] == 0:
            return

        # Deselect the current image
        self.listbox.selection_clear(current_selection[0])

        # Select the next image in the listbox
        next_index = current_selection[0] - 1
        self.listbox.selection_set(next_index)
        # Listbox를 선택하는 이벤트를 발생시켜서 선택된 이미지를 보여줌
        self.listbox.event_generate("<<ListboxSelect>>")
        


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageViewerApp(root)
    root.mainloop()
