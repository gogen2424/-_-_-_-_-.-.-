from flask import Flask, render_template, request, redirect, url_for, flash, session
from database import db, EquipmentRequest, Comment, Review,Masters
from datetime import datetime
from auth import authenticate, ADMIN_USERNAME, ADMIN_PASSWORD, USER_USERNAME, USER_PASSWORD
from forms import CommentForm, ChangeStatusForm


app = Flask(__name__)
app.secret_key ='\xf0?a\x9a\\\xff\xd4;\x0c\xcbHi'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///equipment.db'  # Используем SQLite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Инициализируем базу данных
with app.app_context():
    db.create_all()

# Роут для отображения списка заявок
@app.route('/')
def index():
    if 'logged_in' in session:
        requests = EquipmentRequest.query.all()
        comment_form = CommentForm()
        status_form = ChangeStatusForm()
        return render_template('index.html', requests=requests, comment_form=comment_form, status_form=status_form)
    else:
        return redirect(url_for('login'))

        

# Роут для назначения ответственного за заявку
@app.route('/assign/<int:request_id>', methods=['POST'])
def assign(request_id):
    assigned_to = request.form['assigned_to']
    request_entry = EquipmentRequest.query.get(request_id)
    request_entry.assigned_to = assigned_to
    db.session.commit()
    return redirect(url_for('index'))

# Роут для страницы статистики
@app.route('/statistics')
def statistics():
    responsible_list = db.session.query(EquipmentRequest.assigned_to).distinct().all()
    statistics = {}

    for responsible in responsible_list:
        responsible_name = responsible[0]
        completed_requests = EquipmentRequest.query.filter_by(assigned_to=responsible_name, status='выполнено').all()
        completed_requests_count = len(completed_requests)
        total_time = 0  # Общее время выполнения в секундах

        for request in completed_requests:
            if request.start_date and request.end_date:
                start_time = datetime.strptime(request.start_date, '%Y-%m-%d %H:%M:%S')
                end_time = datetime.strptime(request.end_date, '%Y-%m-%d %H:%M:%S')
                time_diff = (end_time - start_time).total_seconds()
                total_time += time_diff

        average_time = "Не доступно"

        if completed_requests_count > 0:
            average_time_seconds = total_time / completed_requests_count
            average_time = str(int(average_time_seconds / 86400)) + " дней"

        statistics[responsible_name] = {
            "completed_requests_count": completed_requests_count,
            "average_time": average_time,
        }

    # Статистика по типам неисправностей
    fault_type_statistics = {}
    fault_types = db.session.query(EquipmentRequest.fault_type).distinct().all()

    for fault_type in fault_types:
        fault_type_name = fault_type[0]
        completed_requests_count = EquipmentRequest.query.filter_by(fault_type=fault_type_name, status='выполнено').count()
        fault_type_statistics[fault_type_name] = completed_requests_count

    return render_template('statistics.html', statistics=statistics, fault_type_statistics=fault_type_statistics)


# Роут для открытия и редактирования заявки
@app.route('/edit/<int:request_id>', methods=['GET', 'POST'])
def edit(request_id):
    request_entry = EquipmentRequest.query.get(request_id)

    if request.method == 'POST':
        request_entry.request_number = request.form['request_number']
        request_entry.request_date = request.form['request_date']
        request_entry.equipment_name = request.form['equipment_name']
        request_entry.fault_type = request.form['fault_type']
        request_entry.client_name = request.form['client_name']
        request_entry.status = request.form['status']
        request_entry.description = request.form['description']
        request_entry.assigned_to = request.form['assigned_to']
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('edit_request.html', request=request_entry)

# Роут для отображения страницы создания заявки
@app.route('/create_request', methods=['GET', 'POST'])
def create_request():
    if 'logged_in' in session:
        if request.method == 'POST':
            return render_template('create_request.html')
        return render_template('create_request.html')
    else:
        flash('Пожалуйста, войдите, чтобы создать заявку', 'danger')
        return redirect(url_for('login'))

# Роут для поиска заявки по номеру или параметрам
@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_query = request.form['search_query']
        # Поиск заявок по номеру или параметрам
        requests = EquipmentRequest.query.filter(
            (EquipmentRequest.request_number == search_query) |
            (EquipmentRequest.equipment_name.ilike(f"%{search_query}%")) |
            (EquipmentRequest.client_name.ilike(f"%{search_query}%"))
        ).all()
    else:
        requests = EquipmentRequest.query.all()

    return render_template('index.html', requests=requests)

# Роут для создания новой заявки
@app.route('/create', methods=['POST'])
def create():
    request_number = request.form['request_number']
    request_date = request.form['request_date']
    equipment_name = request.form['equipment_name']
    fault_type = request.form['fault_type']
    description = request.form['description']
    client_name = request.form['client_name']
    status = request.form['status']
    created_by = session.get('username', 'unknown')
    request_entry = EquipmentRequest(
        request_number=request_number,
        request_date=request_date,
        equipment_name=equipment_name,
        fault_type=fault_type,
        description=description,
        client_name=client_name,
        status=status,
        created_by=created_by
    )
    db.session.add(request_entry)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if authenticate(username, password):
            # Пользователь успешно аутентифицирован
            # Устанавливаем сессию для авторизации
            session['logged_in'] = True
            session['username'] = username  # Сохраняем имя пользователя в сессии
            flash('Вы успешно вошли', 'success')
            if username == USER_USERNAME:
                return redirect(url_for('user_executions'))
            return redirect(url_for('index'))
        else:
            flash('Неверный логин или пароль', 'danger')
    return render_template('login.html')
    
@app.route('/reviews')
def reviews():
    articles = Review.query.all()
    return render_template('reviews.html', articles = articles)

@app.route('/reviews/<int:review_id>')
def delete_reviews(review_id):
        review = Review.query.get_or_404(review_id)
        try:
            db.session.delete(review)
            db.session.commit()
            return redirect('/reviews')
        except:
             return "Error" 
        

      
@app.route('/masters')
def masters():
    articles = Masters.query.all()
    return render_template('masters.html', articles = articles)
    
@app.route('/create_review', methods = ['GET','POST'])
def create_review():
    if request.method == 'POST':
        intro = request.form['intro']
        rev_text = request.form['text']
        article = Review(rev_text=rev_text, intro=intro)
        try:
            db.session.add(article)
            db.session.commit()
            return redirect(url_for('reviews'))
        
        except:  
            return "Ошибка"  
    else:
        return render_template("create_review.html")
    
@app.route('/masters/<int:master_id>', methods = ['GET','POST'])
def ubdate_master(master_id):
    article = Masters.query.get(master_id)
    if request.method == 'POST':
        article.name = request.form['name']
        article.level = request.form['level']
        article.description = request.form['description']
       
       
        db.session.commit()
        return redirect(url_for('masters'))
        
    else:
        
        return render_template("ubdate_master.html", article=article)

@app.route('/create_masters', methods = ['GET','POST'])
def create_masters():
    if request.method == 'POST':
        name = request.form['name']
        level = request.form['level']
        description = request.form['description']
        article = Masters(name=name, level=level, description=description)
        db.session.add(article)
        db.session.commit()
        return redirect(url_for('masters'))
        
 
           
    else:
        return render_template("create_masters.html")

   
@app.route('/user_executions', methods=['GET', 'POST'])
def user_executions():
    if 'logged_in' in session:
        requests = EquipmentRequest.query.all()
        status_form = ChangeStatusForm()  # Создание экземпляра формы для изменения статуса
        comment_form = CommentForm()  # Создание экземпляра формы для комментариев

        if request.method == 'POST' and status_form.validate_on_submit():
            request_id = request.form['request_id']  # Проверьте, что request доступен здесь
            new_status = status_form.status.data

            # Обновите статус заявки в базе данных
            request_entry = EquipmentRequest.query.get(request_id)
            request_entry.status = new_status
            db.session.commit()
            flash('Статус заявки обновлен', 'success')

        return render_template('user_executions.html', requests=requests, status_form=status_form, comment_form=comment_form)
    else:
        return redirect(url_for('login'))

    
@app.route('/add_comment/<int:request_id>', methods=['POST'])
def add_comment(request_id):
    form = CommentForm()
    if form.validate_on_submit():
        text = form.text.data
        comment_entry = Comment(text=text, request_id=request_id)
        db.session.add(comment_entry)
        db.session.commit()
        flash('Комментарий успешно добавлен', 'success')
    else:
        flash('Ошибка валидации комментария', 'danger')
    return redirect(url_for('user_executions'))

@app.route('/change_status/<int:request_id>', methods=['POST'])
def change_status(request_id):
    form = ChangeStatusForm()
    if form.validate_on_submit():
        new_status = form.status.data
        request_entry = EquipmentRequest.query.get(request_id)
        
        # Проверяем, что текущий пользователь - "user" или "admin"
        if session.get('username') == 'user' or session.get('username') == 'admin':
            request_entry.status = new_status
            db.session.commit()
            flash('Статус заявки изменен', 'success')
        else:
            flash('У вас нет разрешения на изменение статуса заявки', 'danger')
    
    return redirect(url_for('user_executions'))


@app.route('/delete_comment/<int:comment_id>', methods=['POST'])
def delete_comment(comment_id):
    comment = Comment.query.get(comment_id)
    
    # Проверяем, что текущий пользователь - админ
    if session.get('username') == 'admin':
        db.session.delete(comment)
        db.session.commit()
        flash('Комментарий удален', 'success')
    else:
        flash('У вас нет разрешения на удаление комментария', 'danger')
    
    return redirect(url_for('index'))

@app.route('/delete_request/<int:request_id>', methods=['POST'])
def delete_request(request_id):
    if 'logged_in' in session and session.get('username') == 'admin':
        request_entry = EquipmentRequest.query.get(request_id)
        if request_entry:
            db.session.delete(request_entry)
            db.session.commit()
            flash('Заявка удалена', 'success')
        else:
            flash('Заявка не найдена', 'danger')
    else:
        flash('У вас нет прав на удаление заявок', 'danger')
    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    # Выход пользователя
    session.pop('logged_in', None)
    session.pop('username', None)
    flash('Вы успешно вышли', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
