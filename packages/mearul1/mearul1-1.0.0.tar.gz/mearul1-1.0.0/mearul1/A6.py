import tkinter as tk

root = tk.Tk()
root.title("GUI Demo")
root.geometry("500x400")
root.config(bg="lightblue")

tk.Label(root, text="GUI Demo", font=("Arial",20,"bold"), fg="blue", bg="white").pack(pady=10)
tk.Label(root, text="Diff Font Example", font=("Courier",16,"italic"), fg="green", bg="white").pack(pady=5)

f=tk.Frame(root,bg="lightgray",padx=10,pady=10); f.pack(pady=10)
tk.Label(f,text="Name",font=("Arial",12)).grid(row=0,column=0,padx=5,pady=5)
e_name=tk.Entry(f,font=("Arial",12)); e_name.grid(row=0,column=1,padx=5,pady=5)
tk.Label(f,text="Age",font=("Arial",12)).grid(row=1,column=0,padx=5,pady=5)
e_age=tk.Entry(f,font=("Arial",12)); e_age.grid(row=1,column=1,padx=5,pady=5)

tk.Label(root,text="(This label uses place)",font=("Arial",10),fg="red").place(x=150,y=250)

def show(): 
    label_out.config(text=f"Hello {e_name.get()}, Age: {e_age.get()}")

tk.Button(root,text="SuBmit",command=show,bg="orange",font=("Arial",12)).pack(pady=20)
label_out=tk.Label(root,text="",font=("Arial",12),fg="purple",bg="yellow"); label_out.pack()

root.mainloop()
