import smtplib

server = smtplib.SMTP("smtp.gmail.com", 587)
server.starttls()

server.login("shahabdulla09856@gmail.com", "ahbrpzfbvojtixqr")

server.sendmail(
    "shahabdulla09856@gmail.com",
    "abdulah956922@gmail.com",
    "Test"
)

server.quit()