
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DateField, TextAreaField, BooleanField, DecimalField, SelectField
from wtforms.validators import DataRequired, Optional, Length

class EditalForm(FlaskForm):
    numero = StringField('Identificador Legado (Completo)', validators=[DataRequired(), Length(max=50)])
    numero_edital = StringField('Número do Edital', validators=[Optional(), Length(max=20)])
    ano_edital = IntegerField('Ano do Edital', validators=[Optional()])
    empresa = StringField('Empresa / Parceiro', validators=[Optional(), Length(max=100)])
    numero_convenio = StringField('Número do Convênio', validators=[Optional(), Length(max=100)])
    coordenador_geral_proppg = StringField(
        'Coordenador Geral do Projeto / PROPPG',
        validators=[Optional(), Length(max=200)],
    )
    descricao = TextAreaField('Descrição / Objeto', validators=[DataRequired()])
    agencia = StringField('Agência de Fomento / Origem', validators=[DataRequired(), Length(max=50)])
    codigo_projeto = StringField('Código do Projeto', validators=[DataRequired(), Length(max=50)])
    descricao_projeto = TextAreaField('Descrição do Projeto', validators=[DataRequired()])
    processo_sei = StringField('Número do Processo (SEI)', validators=[DataRequired(), Length(max=50)])
    data_inicio = DateField('Início da Vigência', validators=[Optional()])
    data_fim = DateField('Término da Vigência', validators=[Optional()])
    orcamento_total = DecimalField('Orçamento Total (R$)', places=2, validators=[Optional()])
    prestacao_contas = BooleanField('Prestação de Contas Concluída?')
    comentarios = TextAreaField('Observações Internas', validators=[Optional()])
    proap_distribuicao_id = SelectField('Vincular a Recurso PROAP', coerce=int, validators=[Optional()])
