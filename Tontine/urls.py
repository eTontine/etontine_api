from django.urls import path
from Tontine.Views.Carte import *
from Tontine.Views.Groupe import *
from Tontine.Views.AssociateCarte import *
from Tontine.Views.GroupeAssociate import *

urlpatterns = [
    # Carte
    path('create-carte', createCarte, name='create_carte'),
    path('get-cartes/<int:tontinier_id>', getCartes, name='get_cartes'),
    path('get-carte/<int:carte_id>', getCarte, name='get_carte'),
    path('update-carte/<int:carte_id>', updateCarte, name='update_carte'),
    path('delete-carte/<int:carte_id>', deleteCarte, name='delete_carte'),

    # Carte Associate
    path('associateCarte', associateCarte, name='associate_carte'),
    path('getAssociateCartes', getAssociateCartes, name='get_associate_cartes'),
    path('getAssociateCarte/<int:associate_carte_id>', getAssociateCarte, name='get_associate_carte'),
    path('setAssociateCarteUserTontinierStatus/<int:associate_carte_id>', setAssociateCarteUserTontinierStatus, name='set_associate_carte_user_tontinier_status'),

    # Groupe
    path('create-groupe', createGroupe, name='create_groupe'),
    path('get-groupes/<int:tontinier_id>', getGroupes, name='get_groupes'),
    path('get-groupe/<int:groupe_id>', getGroupe, name='get_groupe'),
    path('update-groupe/<int:groupe_id>', updateGroupe, name='update_groupe'),
    path('delete-groupe/<int:groupe_id>', deleteGroupe, name='delete_groupe'),
    path('set-groupe-status/<int:groupe_id>', setGroupeStatus, name='set_groupe_status'),

    # Groupe Associate
    path('add-user-in-groupe', addUserInGroupe, name='add_user_in_groupe'),
    path('validate-reject-invitation/<int:groupe_associate_id>', validateOrRejectGroupeInvitation, name='validate_reject_invitation'),
    path('get-groupe-associate/<int:groupe_associate_id>', getGroupeAssociate, name='get_groupe_associate'),
    path('get-associate-groupes', getAssociateGroupes, name='get_associate_groupes'),
]