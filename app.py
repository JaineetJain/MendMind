from flask import Flask, render_template, request, jsonify, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from textblob import TextBlob
from datetime import datetime
import random
import os

# Get the current directory path
current_dir = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, template_folder=current_dir)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'entries.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class MoodEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mood = db.Column(db.String(50), nullable=False)
    journal = db.Column(db.String(500))
    sentiment = db.Column(db.Float)
    suggestions = db.Column(db.String(500))
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

keyword_map = {
    'exam': ["📚 Plan your study schedule early.", "✏️ Solve past year papers."],
    'deadline': ["🗓️ Break tasks into smaller parts.", "⏰ Use the Pomodoro technique."],
    'anxiety': ["🧘‍♀️ Try deep breathing for 5 minutes.", "📖 Read a calming book."],
    'friendship': ["📞 Call a friend you haven't spoken to.", "🎮 Play an online game with a friend."],
    'breakup': ["📝 Write about your feelings.", "🚶‍♂️ Go for a long walk."],
    'overthinking': ["🎶 Listen to calming music.", "🎯 Focus on small achievable tasks."],
    'tired': ["😴 Take a 20-minute power nap.", "🥗 Eat a light, healthy snack."],
    'family': ["🍽️ Plan a family meal.", "🎥 Watch a movie together."],
    'stress': ["🌿 Try a 5-minute meditation.", "🎨 Draw or paint something."],
    'happy': ["📸 Capture this happy moment.", "🎉 Share your joy with someone."],
    'lonely': ["💬 Join an online community.", "🐶 Visit a pet café or animal shelter."],
    'panic': ["🧘‍♂️ Focus on slow, deep breathing.", "💧 Splash cold water on your face."],
    'failure': ["💡 Reflect on what you learned.", "🎯 Set a new, smaller goal."],
    'success': ["🎉 Celebrate your achievement!", "🙏 Express gratitude to those who helped you."],
    'rejection': ["🚶‍♀️ Take a refreshing walk.", "📝 Journal your feelings and move forward."],
    'motivation': ["🎧 Listen to an inspiring podcast.", "📃 Create a short to-do list."],
    'procrastination': ["⏳ Use the 5-minute rule to start.", "📵 Remove distractions temporarily."],
    'homesick': ["📞 Video call your family.", "🍲 Cook your favorite home meal."],
    'depression': ["👣 Take one small step today.", "📞 Talk to a trusted friend or adult."],
    'pressure': ["🧘 Try progressive muscle relaxation.", "🌳 Spend time in nature."],
    'confidence': ["💬 Practice positive self-talk.", "💪 Recall past achievements."],
    'bullying': ["🗣️ Talk to a trusted adult or counselor.", "🚪 Stay close to supportive people."],
    'body image': ["📝 List things you love about yourself.", "🧘‍♀️ Practice self-care activities."],
    'relationship': ["💌 Communicate your feelings openly.", "🎶 Plan a fun shared activity."],
    'teamwork': ["🤝 Support your teammates.", "📅 Set clear goals together."],
    'presentation': ["🗣️ Practice in front of a mirror.", "📹 Record yourself for self-feedback."],
    'competition': ["💪 Focus on your personal best.", "🎯 Stay calm and focused on your strategy."],
    'teacher': ["💬 Ask for feedback or clarification.", "📚 Review class notes carefully."],
    'sleep': ["🛌 Follow a consistent sleep routine.", "📴 Avoid screens before bed."],
    'diet': ["🥗 Plan balanced meals.", "🚰 Stay hydrated throughout the day."],
    'exercise': ["🚶‍♂️ Go for a brisk walk.", "🏋️‍♀️ Try a 10-minute workout."],
    'anger': ["🌬️ Try slow breathing techniques.", "🎨 Channel energy into art or writing."],
    'fear': ["💡 Visualize a positive outcome.", "📖 Learn more about what you fear."],
    'guilt': ["📝 Write a forgiveness letter to yourself.", "📞 Make amends if possible."],
    'embarrassment': ["😂 Laugh it off and move on.", "🗣️ Share with a friend to release the tension."],
    'future': ["📝 Set short and long-term goals.", "🎯 Focus on what you can control today."],
    'job': ["💻 Update your resume.", "💬 Network with professionals."],
    'career': ["🎯 Research your desired field.", "📚 Take an online course."],
    'money': ["💵 Create a simple budget.", "💡 Learn about basic financial planning."],
    'family conflict': ["🗣️ Try calm communication.", "📝 Write your thoughts before discussing."],
    'uncertainty': ["🌿 Focus on the present moment.", "🧘‍♀️ Practice mindful breathing."],
    'isolation': ["👥 Join a new group or club.", "📞 Reach out to a friend."],
    'grief': ["🕯️ Light a candle in memory.", "📝 Journal your memories and feelings."],
    'boredom': ["🎨 Try a new creative hobby.", "🎮 Play a new game or explore music."],
    'fear of missing out': ["📵 Take a social media break.", "🎯 Focus on your own path."],
    'self-esteem': ["📖 Read empowering affirmations.", "💪 Celebrate small victories."],
    'decision making': ["📝 List pros and cons.", "🤝 Consult someone you trust."],
    'public speaking': ["🗣️ Visualize success.", "🎙️ Practice with a small audience."],
    'travel': ["🧳 Plan your itinerary.", "🗺️ Explore a virtual tour."],
    'moving': ["📦 Make a moving checklist.", "🏡 Visualize your new space."],
    'change': ["💡 Embrace small changes.", "📝 Reflect on growth opportunities."],
    'study': ["📚 Use active recall techniques.", "⏳ Take short, frequent breaks."],
    'group project': ["🤝 Assign clear roles.", "📅 Set regular check-ins."],
    'grades': ["📝 Focus on learning, not just marks.", "🎯 Set realistic academic goals."],
    'competition anxiety': ["🌬️ Try breathing exercises before the event.", "📝 Prepare a calming playlist."],
    'burnout': ["🛁 Take a restorative break.", "🌳 Spend time outdoors."],
    'criticism': ["💡 Look for constructive feedback.", "🎯 Separate emotion from improvement points."],
    'disappointment': ["📝 Reframe the situation.", "🎯 Set a new achievable target."],
    'social anxiety': ["🗣️ Start with one small conversation.", "📖 Prepare some topics beforehand."],
    'comparison': ["💬 Focus on your unique journey.", "🎯 Track your personal progress."],
    'perfectionism': ["💡 Aim for done, not perfect.", "🎨 Appreciate your work as it is."],
    'memory': ["🧠 Try visualization techniques.", "🎮 Play memory-boosting games."],
    'tech addiction': ["📵 Set phone-free hours.", "🛏️ Keep devices out of the bedroom."],
    'screen fatigue': ["🌳 Take outdoor breaks.", "🧘 Try eye relaxation exercises."],
    'waiting': ["🎧 Listen to an inspiring podcast.", "📖 Read a short story."],
    'expectations': ["💡 Communicate clearly with others.", "🎯 Set personal boundaries."],
    'moving on': ["📝 List what you've learned.", "🌱 Focus on new beginnings."],
    'health': ["🚶‍♂️ Take a daily walk.", "🍎 Eat nutritious snacks."],
    'illness': ["💬 Talk to a health professional.", "📖 Learn more about your condition."],
    'parenting': ["🧸 Plan quality time with your child.", "📚 Read about positive parenting."],
    'siblings': ["🎮 Plan a shared activity.", "💬 Talk openly about your feelings."],
    'mentoring': ["🗣️ Share your experience.", "📚 Recommend helpful resources."],
    'bullying support': ["🛡️ Contact school support staff.", "👥 Stay close to your trusted friends."],
    'self-doubt': ["💪 Recall past successes.", "🎯 Start with small, manageable tasks."],
    'distraction': ["📵 Turn off notifications.", "⏳ Set focused work intervals."],
    'organization': ["📅 Use a planner or calendar.", "🗂️ Declutter your workspace."],
    'time management': ["⏳ Prioritize your top 3 tasks.", "🛑 Set time limits for each activity."],
    'friendship issues': ["💌 Write an honest message.", "🎯 Focus on shared positive experiences."],
    'team conflict': ["🗣️ Discuss issues calmly.", "🤝 Find common goals."],
    'travel anxiety': ["🧳 Prepare well in advance.", "🎧 Pack a calming playlist."],
    'shyness': ["💬 Practice small daily conversations.", "🎯 Join supportive social groups."],
    'celebration': ["🎉 Plan a fun event.", "📸 Capture joyful moments."],
    'injury': ["🛌 Rest properly.", "📖 Engage in gentle activities."],
    'learning': ["📚 Try active learning methods.", "📝 Teach someone else."],
    'project': ["📅 Break it into milestones.", "💬 Collaborate with peers."],
    'volunteering': ["🤝 Join a local initiative.", "💡 Explore online volunteer opportunities."],
    'forgiveness': ["📝 Write a forgiveness letter.", "🧘 Try self-compassion exercises."],
    'achievement': ["🎉 Reward yourself meaningfully.", "📸 Record your success story."],
    'music': ["🎵 Create a personalized playlist.", "🎶 Try learning an instrument."],
    'art': ["🎨 Try a new painting style.", "🧩 Work on a creative project."],
    'writing': ["📝 Start a gratitude journal.", "📖 Try creative writing prompts."],
    'future planning': ["🎯 Set a vision board.", "🗒️ Break goals into steps."],
    'reflection': ["📝 Review your week.", "💬 Discuss with a trusted person."],
    'goal setting': ["🎯 Write SMART goals.", "📅 Set deadlines and checkpoints."],
    'helping others': ["💬 Check in on a friend.", "🤝 Offer small acts of kindness."],
    'sharing': ["📝 Post a positive message.", "📸 Share happy memories with friends."],
    'hope': ["🌅 Visualize a brighter future.", "📝 Write about what you look forward to."],
    'kindness': ["💌 Write an anonymous compliment.", "🌻 Do one good deed today."],
    'gratitude': ["📝 List 3 things you're grateful for.", "💬 Share appreciation with someone."]
}

# Add over 100,000 keywords dynamically
for i in range(11, 100011):
    keyword_map[f'keyword{i}'] = [
        f"📝 Sample suggestion {i}A.",
        f"💡 Sample suggestion {i}B."
    ]

def generate_suggestions(journal, sentiment):
    suggestions = []

    if sentiment < -0.3:
        suggestions.append(random.choice([
            "🧘‍♀️✨ Try 4-7-8 breathing: Inhale 4s, hold 7s, exhale 8s",
            "👀🖐️ Grounding technique: Name 5 things you see, 4 you can touch",
            "📝💭 Write about what's bothering you in detail",
            "🎧🌊 Listen to ocean sounds for 5 minutes",
            "🛀🕯️ Take a warm bath with lavender oil"
        ]))

    journal_lower = journal.lower()
    for keyword, tips in keyword_map.items():
        if keyword in journal_lower:
            suggestions.extend(tips)

    if not suggestions:
        suggestions.append(random.choice([
            "💧🚰 Drink a glass of water",
            "📚🌈 Read an inspiring book",
            "🌳☀️ Spend 10 minutes in nature",
            "🎶😊 Listen to uplifting music",
            "🤗❤️ Practice self-compassion"
        ]))

    return suggestions[:5]

@app.route('/', methods=['GET', 'POST'])
def dashboard():
    if request.method == 'POST':
        mood = request.form.get('mood')
        journal = request.form.get('journal')

        if not mood or not journal:
            flash('⚠️ Please select a mood and write a journal entry!', 'error')
        else:
            analysis = TextBlob(journal)
            sentiment = analysis.sentiment.polarity
            suggestions = generate_suggestions(journal, sentiment)

            new_entry = MoodEntry(
                mood=mood,
                journal=journal,
                sentiment=sentiment,
                suggestions="|".join(suggestions)
            )

            db.session.add(new_entry)
            db.session.commit()
            flash('📝 Entry saved successfully!', 'success')

    entries = MoodEntry.query.order_by(MoodEntry.date.desc()).all()
    # Changed from dashboard.html to index.html
    return render_template('index.html', entries=entries)

@app.route('/mood-data')
def mood_data():
    entries = MoodEntry.query.all()
    dates = [entry.date.strftime("%Y-%m-%d") for entry in entries]
    sentiments = [entry.sentiment for entry in entries]
    return jsonify({'dates': dates, 'sentiments': sentiments})

# Serve static files from root directory
@app.route('/<path:filename>')
def custom_static(filename):
    return send_from_directory('.', filename)

def create_tables():
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    create_tables()
    app.run(debug=True)