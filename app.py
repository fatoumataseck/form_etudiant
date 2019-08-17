from flask import Flask,render_template,request,redirect,url_for,flash,jsonify
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
        return '<etudiant %r,%r,%r,%r>' % (self.matricule,self.nom,self.prenom,self.dn)

class Filiere(db.Model):
    __tablename__='filiere'
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    libelle_filiere = db.Column(db.String(80), unique=True, nullable=False)
    def __init__(self,id,libelle_filiere):
        self.id=id
        self.libelle_filiere=libelle_filiere
        
    def __repr__(self):
        return '<filiere %r ,%r>' % (self.id,self.libelle_filiere)

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

#****************************************** generation matricule ************************************************
@app.route('/matricule')
def matricule(): 
    today = datetime.date.today()
    y=today.year
    etu=db.session.query(func.max(Etudiant.id)).one() 
    if etu[0]==None:
        mat="SA-"+str(y)+"-"+str(1)
        id_etu=1
    else:
        mat="SA-"+str(y)+"-"+str(etu[0]+1)
        id_etu=int(etu[0]+1)
    matArray=[]
    matArray.append(mat)
    return jsonify({'etu' : matArray})

#************************************************** remplissage formulaire ******************************************************

@app.route('/',methods=['GET','POST'] )
def acc():
    etu=db.session.query(func.max(Etudiant.id)).one() 
    if etu[0]==None:
        id_etu=1
    else:
        id_etu=int(etu[0]+1)
    fi=db.session.query(Filiere.id,Filiere.libelle_filiere).all()
    if request.method == 'POST':
        matricule=request.form['matricule']
        nom=request.form['nom']
        prenom=request.form['prenom']
        dn=request.form['dn']
        db.session.add(Etudiant(matricule,nom,prenom,dn))
        db.session.commit() 
        
        date_ins=request.form['date_ins']
        annee_aca=request.form['annee_aca']
        id_classe=request.form['classe']
        db.session.add(Inscription(date_ins,annee_aca,id_etu,id_classe))
        db.session.commit() 
        return redirect(url_for('acc'))
        
    return render_template('pages/formulaire.html',fi=fi)

#**************************************** chargement filiere *******************************************************
@app.route('/filiere')
def filiere(): 
    filieres=db.session.query(Filiere.id,Filiere.libelle_filiere).all()
    filiereArray = []
    for filiere in filieres:
        filiereObj = {}
        filiereObj['id'] = filiere.id
        filiereObj['libelle_filiere'] = filiere.libelle_filiere
        filiereArray.append(filiereObj)
    return jsonify({'filieres' : filiereArray})

#**************************************** chargement classe *******************************************************
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

@app.route('/recherche/<mat>')
def recherche(mat): 
    etudiants=db.session.query(Etudiant.matricule,Etudiant.prenom,Etudiant.nom,Etudiant.dn,Inscription.date_ins, Inscription.id_classe,Classe.id_filiere,Classe.libelle_classe,Filiere.libelle_filiere).join(Inscription, Inscription.id_etu == Etudiant.id).join(Classe,Classe.id==Inscription.id_classe).join(Filiere, Filiere.id == Classe.id_filiere).filter(Etudiant.matricule==mat).all()
    print(etudiants)
    recherchearray = []
    for etudiant in etudiants:
        etudiantObj = {}
        etudiantObj['matricule'] = etudiant.matricule
        etudiantObj['nom'] = etudiant.nom
        etudiantObj['prenom'] = etudiant.prenom
        etudiantObj['dn'] = etudiant.dn
        etudiantObj['id_classe'] = etudiant.id_classe
        etudiantObj['libelle_filiere'] = etudiant.libelle_filiere
        etudiantObj['id_filiere'] = etudiant.id_filiere
        etudiantObj['libelle_classe'] = etudiant.libelle_classe
        recherchearray.append(etudiantObj)
    return jsonify({'etudiants' : recherchearray})


if __name__ == "__main__":
    app.run(debug=True)
