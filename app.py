from flask import Flask,render_template,request,redirect,url_for,flash,session, escape,jsonify
from flask_sqlalchemy import *
from sqlalchemy import *
import datetime
from wtforms import *
from flask_wtf import FlaskForm
app= Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:fatou@localhost/form_etudiant'
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = 'secret'

#*****************************************************************************************************************
#                                      CONNEXION BDD ET CREATION TABLE                                      
#***************************************************************************************************************

class Etudiant(db.Model):
    __tablename__='etudiant'
    id= db.Column(db.Integer, primary_key=True,autoincrement=True)
    matricule = db.Column(db.String(80), unique=True, nullable=False)
    nom = db.Column(db.String(120), nullable=False)
    prenom = db.Column(db.String(120), nullable=False)
    dn = db.Column(db.Date, nullable=False)
    def __init__(self,matricule,nom,prenon,dn):
        self.matricule=matricule
        self.prenom=prenon
        self.nom=nom
        self.dn=dn
    def __repr__(self):
        return '<etudiant %r>' % self.matricule,self.nom,self.prenom,self.dn

class Filiere(db.Model):
    __tablename__='filiere'
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    libelle_filiere = db.Column(db.String(80), unique=True, nullable=False)
    def __init__(self,libelle_filiere):
        self.libelle_filiere=libelle_filiere
    def __repr__(self):
        return '<filiere %r>' % self.libelle_filiere

class Classe(db.Model):
    __tablename__='classe'
    id= db.Column(db.Integer, primary_key=True,autoincrement=True)
    libelle_classe = db.Column(db.String(80), unique=True, nullable=False)
    montant_ins = db.Column(db.Integer, nullable=False)
    mensualite = db.Column(db.Integer, nullable=False)
    id_filiere = db.Column(db.Integer, db.ForeignKey('filiere.id'), nullable=False)
    def __init__(self,libelle_classe,montant_ins,mensualite,id_filiere):
        self.libelle_classe=libelle_classe
        self.montant_ins=montant_ins
        self.mensualite=mensualite
        self.id_filiere=id_filiere
    def __repr__(self):
        return '<classe %r,%r,%r,%r>' % (self.libelle_classe,self.montant_ins,self.mensualite,self.id_filiere)

class Inscription(db.Model):
    __tablename__='inscription'
    id= db.Column(db.Integer, primary_key=True,autoincrement=True)
    date_ins = db.Column(db.Date, nullable=False)
    annee_acad = db.Column(db.String, nullable=False)
    id_etu = db.Column(db.Integer, db.ForeignKey('etudiant.id'),nullable=False)
    id_classe = db.Column(db.Integer, db.ForeignKey('classe.id'), nullable=False)
    def __init__(self,date_ins,annee_acad,id_etu,id_classe):
        self.date_ins=date_ins
        self.annee_acad=annee_acad
        self.id_etu=id_etu
        self.id_classe=id_classe
    def __repr__(self):
        return '<inscription %r,%r,%r,%r>' % (self.date_ins,self.annee_acad,self.id_etu,self.id_classe)

db.create_all()

class Form(FlaskForm):
    id_filiere=SelectField('id_filiere',choices=[(1,'AI'),(2,'developpement web'),(3,'data artisan'),(4,'referent digital')])
    classe=SelectField('classe',choices=[])
    montant_ins=TextField('montant_ins')



#*****************************************************************************************************************
#                                    PAGE FORMULAIRE                                      
#***************************************************************************************************************
@app.route('/',methods=['GET','POST'] )
def acc():
    today = datetime.date.today()
    y=today.year
    etu=db.session.query(func.max(Etudiant.id)).one() 
    mat="SA-"+str(y)+"-"+str(etu[0])
    fi=Filiere.query.all()
    clas=Classe.query.all()
    form=Form()
    form.classe.choices=[(classe.id,classe.libelle_classe) for classe in Classe.query.filter_by(id_filiere=1).all()]
    if request.method == 'POST':
        classe = Classe.query.filter_by(id=form.classe.data).first()
        return '<h3>filiere:{},classe:{},montant_ins:{},mensualite:{}</h3>'.format(form.id_filiere.data, classe.libelle_classe,classe.montant_ins,classe.mensualite)
        
    return render_template('pages/formulaire.html',mat=mat,fi=fi,clas=clas,form=form)
 
@app.route('/classe/<id_filiere>')
def classe(id_filiere): 
    classes = Classe.query.filter_by(id_filiere=id_filiere).all()
    classeArray = []
    for classe in classes:
        classeObj = {}
        classeObj['id'] = classe.id
        classeObj['libelle_classe'] = classe.libelle_classe
        classeObj['montant_ins'] = classe.montant_ins
        classeObj['mensualite'] = classe.mensualite

        classeArray.append(classeObj)
    return jsonify({'classes' : classeArray})







if __name__ == "__main__":
    app.run(debug=True)
