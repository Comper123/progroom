from flask import (
    Flask, 
    render_template,
    redirect,
    request,
    url_for
)
# https://qna.habr.com/q/1129874?ysclid=luwtccp25u695089361
from flask_login import (
    LoginManager,
    login_user,
    login_required, 
    logout_user,
    current_user
)
from flask_restful import Api
from django.utils.html import escape, format_html
import data.db_session as db_session

# Импортируем модели данных
from data.users import User
from data.question import Question
from data.answers import Answer
from data.theme import Theme

# Импортируем формы
from forms.register import RegistrationForm
from forms.login import LoginForm
from forms.profile import ProfileForm
from forms.question import QuestionForm
from forms.answer import AnswerForm
from forms.theme import ThemeForm

import answer_api
import like_api


# инициализируем наше flask приложение
app = Flask(__name__)
app.config['SECRET_KEY'] = 'progroom_secret_key'
# Настройки для авторизации пользователей
login_manager = LoginManager()
login_manager.init_app(app)
# Пароль главного админа: admin

# Создаем свое апи
progroom_api = Api(app)
# Доступ ко всем ответам на вопросы
progroom_api.add_resource(answer_api.AnswerListResource, '/api/answers')
# Доступ к одному ответу на вопрос
progroom_api.add_resource(answer_api.AnswerResource, '/api/answers/<int:answer_id>') 


@app.route('/', methods=['POST', 'GET'])
def main():
    """Функция отображения главной страницы"""
    # Создаем сессию к базе данных
    sess = db_session.create_session()
    # Получаем список вопросов
    questions = sess.query(Question).all()[::-1]
    # Формируем словарь с информацией
    data = {
        "questions": questions,
        "dates": {q.id: str(q.create_date).split()[0] for q in questions}
    }
    # Возвращаем отрендеренный шаблон
    return render_template('index.html', data=data)


@app.route('/my_question')
def my_questions():
    """Функция отображения страницы вопросов текущего пользователя"""
    # Создаем сессию к базе данных
    sess = db_session.create_session()
    # Отображение всех вопросов если пользователь - админ
    if current_user.is_superuser:
        questions = sess.query(Question).all()[::-1]
    else:
        # Иначе отображаем все вопросы текущего пользователя
        questions = sess.query(Question).filter(Question.autor == current_user.id)[::-1]
    # Формируем словарь с информацией
    data = {
        "questions": questions,
        "dates": {q.id: str(q.create_date).split()[0] for q in questions}
    }
    # Возвращаем отрендеренный шаблон
    return render_template('my_question.html', data=data) 


@app.route('/register', methods=['POST', 'GET'])
def register():
    """Функция регистрации пользователей"""
    # Создаем форму регистрации
    form = RegistrationForm()
    # Проверяем форму на валидность
    if form.validate_on_submit():
        # Проверяем сходство пароля и его повторения
        if form.pwd1.data != form.pwd2.data:
            return render_template('register.html', title='Регистрация', form=form, message="Пароли не совпадают")
        # Создаем сессию к базе данных
        session = db_session.create_session()
        # Проверяем базу данных на наличие пользователей с такой же почтой как и в форме
        if session.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация', form=form, message="Такой пользователь уже есть")
        # Если все хорошо то создаем пользователя
        user = User(
            name=form.name.data,
            email=form.email.data
        )
        # Устанавливаем пароль пользователя в виде хэша
        user.set_password(form.pwd1.data)
        # Добавляем пользователяы
        session.add(user)
        # Подтверждаем сессию к бд
        session.commit()
        # Авторизуем пользователя
        login_user(user)
        # Возвращаем отрендеренный шаблон главной сайта
        return redirect('/')
    # Возвращаем отрендеренный шаблон регистрации
    return render_template('register.html', title='Регистрация', form=form)


# Функция для передачи на любую страницу текущего пользователя
@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    # Возвращаем объект бд с информацией о текущем пользователе
    return db_sess.query(User).filter(User.id == user_id).first()


@app.route('/login', methods=['POST', 'GET'])
def login():
    """Функция авторизации пользователей"""
    # Создаем обьект формы авторизации
    form = LoginForm()
    # Если форма валидна
    if form.validate_on_submit():
        # Создаем подключение к бд
        db_sess = db_session.create_session()
        # получаем пользователя по почте
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        # Если пароль из формы сошелся с паролем в бд (по хэшу)
        if user and user.check_password(form.password.data):
            # Авторизуем пользователя
            login_user(user, remember=form.remember_me.data)
            # Возвращаем отрендеренный шаблон главной сайта
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    """Функция выхода пользователя из системы"""
    # Выходим из аккаунта пользователя
    logout_user()
    # Возвращаем главную страницу
    return redirect("/")


@app.route('/profile', methods=['POST', 'GET'])
def profile():
    """Функция страницы профиля пользователя"""
    # Создаем обьект формы заполнения профиля
    form = ProfileForm()
    # Если мы получаем страницу
    if request.method == "GET":
        # Получаем пользователя из базы данных
        sess = db_session.create_session()
        user = sess.query(User).filter(User.id == current_user.id).first()
        # Устанавливаем в форму ланные пользователя
        form.email.data = user.email
        form.name.data = user.name
    # В случае верной отправки формы
    if form.validate_on_submit():
        # Получаем пользователя из базы данных
        sess = db_session.create_session()
        user = sess.query(User).filter(User.id == current_user.id).first()
        # Заменяем данные
        user.name = form.name.data
        user.email = form.email.data
        sess.commit()
        # Возвращем главную страницу
        return redirect('/')
    # Передаем данные в шаблон
    user = sess.query(User).filter(User.id == current_user.id).first()
    # Формируем словарь с данными
    data = {
        "form": form,
        "start_lvl": min((user.exp // 100 + 1), 26),
        "end_lvl": min((user.exp // 100 + 2), 27),
        "exp": user.exp % 100 if user.exp < 2700 else user.exp - 2700,
        "start_rang": f'static/img/rang/rang{min((user.exp // 100 + 1), 26)}.png',
        "end_rang": f'static/img/rang/rang{min((user.exp // 100 + 2), 27)}.png',
    }
    # Вовращаем отрендеренный шаблон страницы профиля пользователя
    return render_template('profile.html', data=data)


@app.route('/create_question', methods=['POST', 'GET'])
def create_question():
    """Функция страницы формирования вопроса"""
    # Создаем форму для вопроса
    form = QuestionForm()
    # При отправке формы на сервер
    if request.method == "POST" and form.validate_on_submit():
        # Создаем сессию к бд
        sess = db_session.create_session()
        # получаем тему из таблицы тем
        t_id = sess.query(Theme).filter(Theme.title == form.theme.data).first().id
        # Создаем объект вопроса
        q = Question(
            title=form.title.data,
            # content=escape(form.content.data),
            content=form.content.data,
            autor=current_user.id,
            theme_id=t_id
        )
        # Добавляем вопрос в бд
        sess.add(q)
        # Подтверждаем сессию к бд
        sess.commit()
        sess2 = db_session.create_session()
        q1 = sess2.query(Question).filter(Question.title == form.title.data).first()
        # request.files[] по тому названию переменная изображения в форме
        if 'img' in request.files:
            f = request.files['img']
            # В форме обязательно указать enctype="multipart/form-data" для загрузки медиа
            if f:
                f.save(f'static/img/questions/{q1.id}.png')
                q1.img = f"{q1.id}.png"
        sess2.commit()
        return redirect('/')
    return render_template('create_question.html', form=form)


# ! Проблема с автозаполнением поля фотография
@app.route('/edit_question/<int:q_id>', methods=['POST', 'GET'])
def edit_question(q_id):
    """Функция страницы редактирования вопроса"""
    # Создаем форму
    form = QuestionForm()
    # При загрузке страницы
    if request.method == "GET":
        sess = db_session.create_session()
        question = sess.query(Question).filter(Question.id == q_id).first()
        # Если пользователь не совпадает с создателем вопроса
        if question.autor != current_user.id and not current_user.is_superuser:
            return redirect('/')
        form.title.data = question.title
        form.content.data = question.content
        # Заполняем поле темы в форме
        t_title = sess.query(Theme).filter(Theme.id == question.theme_id).first().title
        form.theme.data = t_title
    # При успешной отправке формы редатируем вопрос
    if request.method == "POST" and form.validate_on_submit():
        sess = db_session.create_session()
        qq = sess.query(Question).filter(Question.title == form.title.data).first()
        if qq and qq.id != q_id:
            return render_template('create_question.html', form=form, message="Такой вопрос уже есть")
        question = sess.query(Question).filter(Question.id == q_id).first()
        question.title = form.title.data
        question.content = form.content.data
        # Изменяем тему вопроса
        t_id = sess.query(Theme).filter(Theme.title == form.theme.data).first().id
        question.theme_id = t_id
        # request.files[] по тому названию переменная изображения в форме
        if 'img' in request.files:
            f = request.files['img']
            # В форме обязательно указать enctype="multipart/form-data" для загрузки медиа
            if f:   
                f.save(f'static/img/questions/{qq.id}.png')
                question.img = f"{qq.id}.png"
        sess.commit()
        return redirect('/')
    return render_template('create_question.html', form=form)


@app.route('/delete_question/<int:q_id>')
def delete_question(q_id):
    """Функция удаления вопроса"""
    sess = db_session.create_session()
    question = sess.query(Question).filter(Question.id == q_id).first()
    # Если пользователь не совпадает с создателем вопроса
    if question.autor != current_user.id and not current_user.is_superuser:
        return redirect('/')
    db_sess = db_session.create_session()
    q = db_sess.query(Question).filter(Question.id == q_id).first()
    if q:
        # Получаем ответы на вопрос связанные с удаляемым вопросом
        answers = db_sess.query(Answer).filter(Answer.question == q_id).all()
        # Удаляем связанные ответы
        for an in answers:
            db_sess.delete(an)
        # Удаляем вопрос
        db_sess.delete(q)
        db_sess.commit()
    return redirect('/my_question')


@app.route('/question/<int:q_id>', methods=['POST', 'GET'])
def question(q_id):
    """Функция отображения конкретного вопроса"""
    answer_form = False
    # Создаем словарь с данными
    data = {}
    # Создаем сессию к бд
    sess = db_session.create_session()
    # Получаем вопрос из бд
    q = sess.query(Question).filter(Question.id == q_id).first()
    # Получаем автора из бд
    autor = sess.query(User).filter(User.id == q.autor).first()
    q.content = format_html(q.content)
    data['question'] = q
    data['date'] = str(q.create_date).split()[0]
    data['autor'] = autor.name
    if q.img is not None:
        data['img'] = f'/static/img/questions/{q.img}'
    # Проверяем авторизован ли пользователь
    if current_user.is_authenticated:
        # Проверяем не является ли текщий пользователь автором своего же вопроса
        if current_user.id != q.autor:
            # Форма ответа на вопрос
            answer_form = AnswerForm()
            data['answer_form'] = answer_form
            if request.method == 'POST':
                answer_sess = db_session.create_session()
                answer = Answer(
                    text=answer_form.text.data,
                    autor=current_user.id,
                    question=q_id
                )
                answer_sess.add(answer)
                answer_sess.commit()
                # !Изменяем рейтинг отвечавшего пользователя
                s = db_session.create_session()
                u = s.query(User).filter(User.id == current_user.id).first()
                u.give_experience(10)
                s.commit()
                return redirect(f'/question/{q_id}')
    if request.method == "GET":
        answers_sess = db_session.create_session()
        ans = answers_sess.query(Answer).filter(Answer.question == q_id).all()[::-1]
        if ans:
            data['answers'] = ans
            data['answers_date'] = {a.id: str(a.date).split()[0] for a in ans}
            data['answers_users'] = {u.id: u for u in answers_sess.query(User).all()}
    return render_template('question.html', data=data, title=f'Вопрос №{q.id}')


@app.route('/delete_answer/<int:a_id>')
def delete_answer(a_id):
    """Функция удаления ответа на вопрос"""
    sess = db_session.create_session()
    answer = sess.query(Answer).filter(Answer.id == a_id).first()
    # Если пользователь не совпадает с создателем вопроса
    if answer.autor != current_user.id and not current_user.is_superuser:
        return redirect('/')
    if not current_user.is_authenticated:
        return redirect('/')
    if answer:
        # !Изменяем рейтинг отвечавшего пользователя
        s = db_session.create_session()
        u = s.query(User).filter(User.id == answer.autor).first()
        u.take_experience(10)
        s.commit()
        sess.delete(answer)
        sess.commit()
    return redirect(f'/question/{answer.question}')


@app.route('/like_answer/a_id=<int:a_id>&q_id=<int:q_id>')
def like_answer(a_id, q_id):
    """Функция лайка ответа на вопрос автором вопроса"""
    sess = db_session.create_session()
    q = sess.query(Question).filter(Question.id == q_id).first()
    if not current_user.is_authenticated or q.autor != current_user.id:
        return redirect(f'/question/{q_id}')
    a = sess.query(Answer).filter(Answer.id == a_id).first()
    # На случай накрута пользователем опыта
    if a.is_like_autor:
        return redirect(f'/question/{q_id}')
    u = sess.query(User).filter(User.id == a.autor).first()
    # Начисляем опыт автору ответа
    u.give_experience(10)
    a.is_like_autor = True
    sess.commit()
    return redirect(f'/question/{q_id}')


@app.route('/like_answer_user/a_id=<int:a_id>&q_id=<int:q_id>', methods=['POST', 'GET'])
def like_answer_user(a_id, q_id):
    """Функция лайка ответа на вопрос других участников форума"""
    sess = db_session.create_session()
    a = sess.query(Answer).filter(Answer.id == a_id).first()
    if not current_user.is_authenticated or current_user.id in a.liked():
        return redirect(f'/question/{q_id}')
    a.like(current_user.id)
    u = sess.query(User).filter(User.id == a.autor).first()
    u.give_experience(5)
    sess.commit()
    return redirect(f'/question/{q_id}')
    # return redirect(request.referrer)


@app.route('/dislike_answer/a_id=<int:a_id>&q_id=<int:q_id>', methods=['POST', 'GET'])
def dislike_answer(a_id, q_id):
    """Функция дизлайка ответа на вопрос других участников форума"""
    sess = db_session.create_session()
    a = sess.query(Answer).filter(Answer.id == a_id).first()
    if not current_user.is_authenticated or not current_user.id in a.liked():
        return redirect(f'/question/{q_id}')
    a.dislike(current_user.id)
    u = sess.query(User).filter(User.id == a.autor).first()
    u.take_experience(5)
    sess.commit()
    return redirect(f'/question/{q_id}')
    # return redirect(request.referrer)


@app.route('/reiting')
def reiting():
    """Функция отображения рейтинга участников форума"""
    sess = db_session.create_session()
    users = sorted(sess.query(User).all(), key=lambda x: x.exp, reverse=True)
    return render_template('reiting.html', users=users)


@app.route('/themes')
def themes():
    """Функция отображения всех тем вопросов форума"""
    # Создаем сессию бд
    sess = db_session.create_session()
    # Получаем все темы вопросов 
    thms = sess.query(Theme).all()
    # Возвращаем шаблон страницы со всеми темами
    return render_template('themes.html', thms=thms)


@app.route('/themes/<int:t_id>')
def theme(t_id):
    """Функция отображения конкретной темы"""
    # Создаем сессию бд
    sess = db_session.create_session()
    # Получаем тему из бд по ее id 
    t = sess.query(Theme).filter(Theme.id == t_id).first()
    questions = sess.query(Question).filter(Question.theme_id == t_id).all()
    data = {
        'theme': t,
        'questions': questions,
        "dates": {q.id: str(q.create_date).split()[0] for q in questions},
    }
    return render_template('theme.html', data=data)


@app.route('/add_theme', methods=['POST', 'GET'])
def add_theme():
    """Функция добавления отдельной темы вопросов"""
    # Создаем форму
    form = ThemeForm()
    # Обработка отправки формы
    if request.method == "POST" and form.validate_on_submit():
        sess = db_session.create_session()
        if sess.query(Theme).filter(Theme.title == form.title.data).first():
            return render_template('create_theme.html', form=form, message="Такая тема уже есть")
        # Создаем обьект темы
        t = Theme(
            title=form.title.data,
            description=form.description.data,
            creator=current_user.id
        )
        sess.add(t)
        sess.commit()
        return redirect('/themes')
    return render_template('create_theme.html', form=form)


@app.errorhandler(404)
def not_found(_):
    """Обработчик ошибки 404"""
    # Возвращаем шаблон для ошибки
    return render_template('404.html')


@app.errorhandler(400)
def bad_request(_):
    """Обработчик ошибки 400"""
    # Возвращаем шаблон для ошибки
    return render_template('404.html')


def main():
    # Создаем доступ к базе данных
    db_session.global_init('db/forum.db')
    # Запускаем приложение
    app.run()


if __name__ == "__main__":
    # Запуск проекта
    app.register_blueprint(like_api.blueprint)
    # Вызываем главную функцию
    main()