import datetime as dt

while True:
    print("\n1.Current Date & Time  2.Day of Week  3.Date Diff  4.Exit")
    ch = input("Choice (1-4): ")

    if ch=='1':
        now = dt.datetime.now()
        print("DateTime:", now.strftime("%Y-%m-%d %H:%M:%S"))
        print("Date:", now.date(), "Time:", now.time().strftime("%H:%M:%S"))

    elif ch=='2':
        d = input("Enter date (YYYY-MM-DD): ")
        try: print("Day:", dt.datetime.strptime(d,"%Y-%m-%d").strftime("%A"))
        except: print("Invalid date!")

    elif ch=='3':
        d1 = input("First date: "); d2 = input("Second date: ")
        try:
            diff = abs((dt.datetime.strptime(d2,"%Y-%m-%d") - dt.datetime.strptime(d1,"%Y-%m-%d")).days)
            print(f"Diff: {diff} days")
        except: print("Invalid date")

    elif ch=='4': 
        print("Exiting..."); break
    else: print("Invalid choice!")
