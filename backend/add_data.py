from app import db, Video

# Create a new video entry
new_video = Video(
    title="Sample Video",
    description="This is a sample video description",
    thumbnail="sample-thumbnail.jpg",
    video_path="uploads/sample-video.mp4",
    hashtags="sample, test"
)

# Add and commit to the database
db.session.add(new_video)
db.session.commit()

print("Video added successfully!")
