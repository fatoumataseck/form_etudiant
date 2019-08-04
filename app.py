from flask import Flask,render_template,request,redirect,url_for,flash,session, escape
from flask_sqlalchemy import *
from sqlalchemy import *
import datetime
app= Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:fatou@localhost/form_etudiant'
db = SQLAlchemy(app)
app.secret_key=b'flash message'
app.config['UPLOAD_FOLDER']='/var/www/html/sonatel/static/font/profiles/'

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
        return '<etudiant %r,%r,%r,%r>' % (self.matricule,self.nom,self.prenom,self.dn)

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

#*****************************************************************************************************************
#                                    PAGE FORMULAIRE                                      
#***************************************************************************************************************
@app.route('/' )
def acc():
    today = datetime.date.today()
    y=today.year
    print(y)
    etu=db.session.query(func.max(Etudiant.id)).one() 
    mat="SA-"+str(y)+"-"+str(etu[0])
    fi=Filiere.query.all()
    clas=Classe.query.all()
    return render_template('pages/formulaire.html',mat=mat,fi=fi,clas=clas)

#*****************************************************************************************************************
#                                    INSERTION                                     
#***************************************************************************************************************

@app.route('/', methods=['POST'])
def ins():
    matricule=request.form['matricule']
    nom=request.form['nom']
    prenom=request.form['prenom']
    dn=request.form['dn']
    #db.session.add(Etudiant(matricule,nom,prenom,dn))
    #db.session.commit() 

    """#filiere=request.form['filiere']
    classe=request.form['classe']
    montant=request.form['montant']
    mensualite=request.form['mensualite']
    total=request.form['total']
    date_ins=request.form['date_ins']
    annee_aca=request.form['annee_aca']
    db.session.add(Inscription(date_ins,annee_aca,id_etu,classe))
    db.session.commit() 
    """
    return redirect(url_for('acc'))

if __name__ == "__main__":
    app.run(debug=True)
