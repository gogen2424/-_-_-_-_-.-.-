from flask_wtf import FlaskForm
from wtforms import TextAreaField, SelectField
from wtforms.validators import DataRequired

class CommentForm(FlaskForm):
    text = TextAreaField('Комментарий', validators=[DataRequired()])
class ChangeStatusForm(FlaskForm):
    status = SelectField('Статус', choices=[('в ожидании', 'В ожидании'), ('в работе', 'В работе'), ('выполнено', 'Выполнено')])
