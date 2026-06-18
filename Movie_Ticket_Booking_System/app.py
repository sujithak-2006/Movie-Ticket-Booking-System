from flask import Flask, render_template, request, redirect, session, jsonify
import mysql.connector

app = Flask(__name__)
app.secret_key = "moviebooking123"

# ================= DATABASE CONNECTION =================
import os

db_host = os.environ.get("DB_HOST", "localhost")
db_user = os.environ.get("DB_USER", "root")
db_password = os.environ.get("DB_PASSWORD", "Tamil@123")
db_name = os.environ.get("DB_NAME", "movie_booking")

db = mysql.connector.connect(
    host=db_host,
    user=db_user,
    password=db_password,
    database=db_name
)

cursor = db.cursor(buffered=True, dictionary=True)
print("Connected to MySQL database successfully!")


# ================= HOME ROUTE =================
@app.route('/')
def home():
    cursor.execute("SELECT * FROM movies")
    db_movies = cursor.fetchall()
    return render_template('index.html', username=session.get('username'), catalog=db_movies)


# ================= REGISTER =================
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        cursor.execute(
            "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
            (username, email, password)
        )
        db.commit()
        return redirect('/login')

    return render_template('register.html')


# ================= LOGIN =================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        cursor.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, password))
        user = cursor.fetchone()

        if user:
            session['user_id'] = user.get('user_id')
            session['username'] = user.get('username')
            session['email'] = user.get('email')
            return redirect('/')
        else:
            return "Invalid Email or Password"

    return render_template('login.html')


# ================= LOGOUT =================
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


# ================= PROFILE =================
@app.route('/profile')
def profile():
    if not session.get('username'):
        return redirect('/login')

    return render_template(
        'profile.html',
        username=session.get('username'),
        email=session.get('email')
    )


# ================= MOVIE DETAILS =================
@app.route('/movie/<string:movie_name>')
def movie_details(movie_name):
    normalized_name = movie_name.replace('-', ' ')

    cursor.execute("""
        SELECT * FROM movies 
        WHERE LOWER(TRIM(movie_name)) = LOWER(TRIM(%s))
    """, (normalized_name,))

    movie = cursor.fetchone()

    if not movie:
        return f"<h3>Error: Movie '{normalized_name}' not found.</h3>"

    movie_data = {
        "title": movie.get('movie_name'),
        "genre": movie.get('genre'),
        "language": movie.get('language'),
        "duration": movie.get('duration'),
        "price": movie.get('price'),
        "image": movie.get('poster_url'),
        "description": movie.get('description') if movie.get('description') else "No plot summary available."
    }

    session['movie_name'] = movie_data["title"].lower()

    return render_template('movie_details.html', movie=movie_data)


# ================= USER SIDE: BOOKING PAGE (DYNAMICALLY FETCH AVAILABLE DATES) =================
@app.route('/booking')
def booking():
    movie_name = request.args.get('movie')
    movie_title = "Select Seats"
    available_dates = []

    if movie_name:
        normalized_name = movie_name.replace('-', ' ')
        
        cursor.execute("""
            SELECT movie_id, movie_name, price FROM movies 
            WHERE LOWER(TRIM(movie_name)) = LOWER(TRIM(%s))
        """, (normalized_name,))
        movie_data = cursor.fetchone()
        
        if movie_data:
            movie_title = movie_data.get('movie_name')
            m_id = movie_data.get('movie_id')
            
            # ✅ FIXED: Update the session token immediately when landing on the booking page 
            # to prevent fallback data leaking onto ticket checkouts!
            session['movie_name'] = movie_title.lower()
            
            # Query ONLY the unique upcoming dates the admin scheduled for this movie
            cursor.execute("""
                SELECT DISTINCT show_date FROM shows 
                WHERE movie_id = %s AND show_date >= CURDATE()
                ORDER BY show_date ASC
            """, (m_id,))
            date_records = cursor.fetchall()
            
            available_dates = [str(d['show_date']) for d in date_records]

    return render_template('booking.html', movie_title=movie_title, available_dates=available_dates)

# ================= DYNAMIC TIMINGS FETCH API =================
@app.route('/api/get_timings')
def get_timings():
    movie_name = request.args.get('movie_name')
    chosen_date = request.args.get('chosen_date')
    
    normalized_name = movie_name.replace('-', ' ')

    query = """
        SELECT s.show_id, s.show_time, s.price FROM shows s
        INNER JOIN movies m ON s.movie_id = m.movie_id
        WHERE LOWER(TRIM(m.movie_name)) = LOWER(TRIM(%s)) AND s.show_date = %s
    """
    cursor.execute(query, (normalized_name, chosen_date))
    available_slots = cursor.fetchall()

    return jsonify(available_slots)


# ================= SAVE BOOKING =================
@app.route('/save_booking', methods=['POST'])
def save_booking():
    session['seats'] = request.form.get('seats')
    session['show_time'] = request.form.get('show_time')
    session['booking_date'] = request.form.get('booking_date')
    session['amount'] = request.form.get('amount')
    session['show_id'] = request.form.get('show_id') 
    
    return redirect('/payment')


# ================= PAYMENT =================
@app.route('/payment')
def payment():
    return render_template('payment.html')


# ================= SAVE PAYMENT =================
@app.route('/save_payment', methods=['POST'])
def save_payment():
    session['payment_method'] = request.form.get('payment_method')
    return redirect('/success')


# ================= SUCCESS =================
@app.route('/success')
def success():
    if not session.get('email'):
        return redirect('/login')

    movie_name = session.get('movie_name', 'None')
    seats = session.get('seats', 'None')
    show_time = session.get('show_time', 'None')
    chosen_date = session.get('booking_date', 'Today')
    amount = session.get('amount', '0')
    show_id = session.get('show_id')
    payment_method = session.get('payment_method', 'Card Payment')

    cursor.execute("SELECT user_id FROM users WHERE email=%s", (session['email'],))
    user = cursor.fetchone()
    user_id = user.get('user_id') if user else 1

    cursor.execute("SELECT movie_id FROM movies WHERE LOWER(TRIM(movie_name)) = LOWER(TRIM(%s))", (movie_name,))
    movie_record = cursor.fetchone()
    movie_id = movie_record.get('movie_id') if movie_record else 1

    cursor.execute("""
        INSERT INTO bookings (user_id, movie_id, show_id, show_time, seat_numbers, amount, booking_date)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (user_id, movie_id, show_id if show_id else None, show_time, seats, amount, chosen_date))
    db.commit()

    generated_ticket_id = cursor.lastrowid

    return render_template('success.html', 
                           movie_title=movie_name.title(), 
                           seats_list=seats, 
                           time_slot=show_time, 
                           pay_method=payment_method, 
                           total_paid=amount, 
                           ticket_id=generated_ticket_id)


# ================= MY BOOKINGS HISTORY ROUTE =================
@app.route('/my_bookings')
def my_bookings():
    if not session.get('user_id'):
        return redirect('/login')

    user_id = session.get('user_id')

    query = """
        SELECT 
            b.booking_id, 
            b.show_time, 
            b.seat_numbers, 
            b.amount, 
            b.status,
            b.booking_date,
            m.movie_name, 
            m.poster_url 
        FROM bookings b
        INNER JOIN movies m ON b.movie_id = m.movie_id
        WHERE b.user_id = %s
        ORDER BY b.booking_id DESC
    """
    
    cursor.execute(query, (user_id,))
    user_history = cursor.fetchall()

    return render_template('my_bookings.html', username=session.get('username'), bookings=user_history)


# ================= ADMIN SIDE: ADD NEW MOVIES TO CATALOG =================
@app.route('/admin/add_movie', methods=['GET', 'POST'])
def add_movie():
    if not session.get('email') or session.get('email') != 'admin@moviehub.com':
        return "<h3>Unauthorized Access: Admin privileges required.</h3>", 403

    if request.method == 'POST':
        movie_name = request.form.get('movie_name')
        genre = request.form.get('genre')
        language = request.form.get('language')
        duration = request.form.get('duration')
        price = request.form.get('price')
        poster_url = request.form.get('poster_url') 

        cursor.execute("""
            INSERT INTO movies (movie_name, genre, language, duration, price, poster_url)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (movie_name, genre, language, duration, price, poster_url))
        db.commit()
        return "<script>alert('New movie added to catalog successfully!'); window.location.href='/admin/add_movie';</script>"

    return render_template('admin_add_movie.html')


# ================= MASTER ADMIN: ADD SHOW TIMELINES FORM =================
@app.route('/admin/add_show', methods=['GET', 'POST'])
def add_show():
    if not session.get('email') or session.get('email') != 'admin@moviehub.com':
        return "<h3>Unauthorized Access: Admin privileges required.</h3>", 403

    if request.method == 'POST':
        movie_id = request.form.get('movie_id')
        show_date = request.form.get('show_date')   
        show_time = request.form.get('show_time')   
        price = request.form.get('price')

        cursor.execute("""
            INSERT INTO shows (movie_id, show_date, show_time, price)
            VALUES (%s, %s, %s, %s)
        """, (movie_id, show_date, show_time, price))
        db.commit()
        
        return "<script>alert('Show published successfully!'); window.location.href='/admin/add_show';</script>"

    cursor.execute("SELECT movie_id, movie_name FROM movies ORDER BY movie_id DESC")
    all_movies = cursor.fetchall()
    return render_template('admin_add_show.html', movies=all_movies)


# ================= ADMIN: SIMULATE POPULATING SHOWS =================
@app.route('/admin/setup_shows')
def setup_shows():
    try:
        cursor.execute("INSERT INTO shows (movie_id, show_date, show_time, price) VALUES (1, CURDATE(), '10:00 AM', 180)")
        cursor.execute("INSERT INTO shows (movie_id, show_date, show_time, price) VALUES (1, CURDATE(), '5:00 PM', 180)")
        cursor.execute("INSERT INTO shows (movie_id, show_date, show_time, price) VALUES (3, CURDATE(), '1:30 PM', 180)")
        db.commit()
        return "<h3>Success: Test shows added for today!</h3>"
    except Exception as e:
        return f"<h3>Status: Setup skipped or error occurred: {str(e)}</h3>"


# ================= MASTER BACKEND: BATCH DELETE SELECTED HISTORY LOGS =================
@app.route('/delete_selected_bookings', methods=['POST'])
def delete_selected_bookings():
    if not session.get('user_id'):
        return redirect('/login')

    # Read the data rows mapped array sent via the checkbox form post names
    selected_ids = request.form.getlist('booking_ids')

    if selected_ids:
        # Generate safe matching variable binding parameters dynamically to clear targets safely
        format_strings = ','.join(['%s'] * len(selected_ids))
        query = f"DELETE FROM bookings WHERE booking_id IN ({format_strings}) AND user_id = %s"
        
        # Security parameter injection containment pairing
        query_params = list(selected_ids) + [session['user_id']]
        
        cursor.execute(query, query_params)
        db.commit()

    return redirect('/my_bookings')

# ================= GLOBAL MOVIES CATALOG DISCOVERY LINK =================
@app.route('/movies')
def movies_catalog():
    # Fetch all records dynamically from database catalog table layout rows
    cursor.execute("SELECT * FROM movies ORDER BY movie_name ASC")
    all_movies = cursor.fetchall()
    return render_template('movies.html', catalog=all_movies)

# ================= SINGLE TICKET CANCELLATION ENGINE =================
@app.route('/cancel_booking/<int:booking_id>')
def cancel_booking(booking_id):
    # Verify user authentication sequence state
    if not session.get('user_id'):
        return redirect('/login')

    try:
        # Instead of deleting the record completely, change its status to 'Cancelled'
        # to ensure it preserves your layout structure gracefully
        query = "UPDATE bookings SET status = 'Cancelled' WHERE booking_id = %s AND user_id = %s"
        cursor.execute(query, (booking_id, session['user_id']))
        db.commit()
        
    except Exception as e:
        db.rollback()
        print(f"Database error during reservation cancel operation sequence: {e}")

    # Seamlessly return right back to your updated dashboard view
    return redirect('/my_bookings')

if __name__ == '__main__':
    app.run(debug=True)
