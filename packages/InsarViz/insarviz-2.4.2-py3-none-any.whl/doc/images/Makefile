VIDEOS := $(wildcard *.mp4)

%_thumbnail.jpg: %.mp4
	rm $@
	ffmpeg -i $< -ss 00:00:00 -frames:v 1 $@

thumbnails: $(VIDEOS:%.mp4=%_thumbnail.jpg)
