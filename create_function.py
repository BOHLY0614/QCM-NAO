res = "self.chapter_files = ["


for i in range(1,15):
    if i==5 or i==10 or i==11:
        None
    else:
        res+= "\"JSON/Seminar " + str(i) + ".json\"," 

print(res)


# "JSON/Seminar Grile.json","JSON/Seminar Partial","JSON/Seminar 1.json","JSON/Seminar 2.json","JSON/Seminar 3.json","JSON/Seminar 4.json","JSON/Seminar 6.json","JSON/Seminar 7.json","JSON/Seminar 8.json","JSON/Seminar 9.json","JSON/Seminar 12.json","JSON/Seminar 13.json","JSON/Seminar 14.json"