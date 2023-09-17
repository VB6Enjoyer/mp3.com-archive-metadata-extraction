import os, eyed3, xlsxwriter;

path = input("Input the path to the mp3s: ");
workbook = xlsxwriter.Workbook("mp3s.xlsx");
worksheet = workbook.add_worksheet();
i = 1;

# Iterates through the folder.
for filename in os.listdir(path):
    path_to_file = path + "\\" + filename; # This is the path to the file.
    
    if not path_to_file.endswith(".mp3"):
        print(filename, "is not an mp3. Skipping.");
        continue;
    
    mp3_file = eyed3.load(path_to_file); # Loads the mp3 file.

    if mp3_file != None:
        if hasattr(mp3_file.tag, 'artist'):
            worksheet.write("A" + str(i), mp3_file.tag.artist);
        if hasattr(mp3_file.tag, 'title'):
            worksheet.write("B" + str(i), mp3_file.tag.title);
    else:
        print(filename, "seems to be corrupt. Skipping.");

    worksheet.write("C" + str(i), filename);
    print("Processed", filename + ".", i, "files processed");
    i += 1;

print("Created a file with", i, "entries");

workbook.close()

# VB6Enjoyer, 2022
