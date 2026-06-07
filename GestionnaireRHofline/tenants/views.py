"""
Vues pour l'inscription et la gestion des tenants
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import IntegrityError
from .services import TenantProvisioningService
from .models import Client


def inscription_entreprise(request):
    """
    Vue d'inscription d'une nouvelle entreprise
    Crée automatiquement le schéma et l'utilisateur admin
    """
    if request.method == 'POST':
        # Récupérer les données du formulaire
        nom_entreprise = request.POST.get('nom_entreprise', '').strip()
        email_entreprise = request.POST.get('email_entreprise', '').strip()
        telephone = request.POST.get('telephone', '').strip()
        adresse = request.POST.get('adresse', '').strip()
        ville = request.POST.get('ville', '').strip()
        nif = request.POST.get('nif', '').strip() or None
        num_cnss = request.POST.get('num_cnss', '').strip() or None
        
        # Données admin
        admin_nom = request.POST.get('admin_nom', '').strip()
        admin_prenoms = request.POST.get('admin_prenoms', '').strip()
        admin_email = request.POST.get('admin_email', '').strip()
        admin_password = request.POST.get('admin_password', '')
        admin_password_confirm = request.POST.get('admin_password_confirm', '')
        
        # Validation
        errors = []
        
        if not nom_entreprise:
            errors.append("Le nom de l'entreprise est requis")
        if not email_entreprise:
            errors.append("L'email de l'entreprise est requis")
        if not admin_email:
            errors.append("L'email de l'administrateur est requis")
        if not admin_password:
            errors.append("Le mot de passe est requis")
        if admin_password != admin_password_confirm:
            errors.append("Les mots de passe ne correspondent pas")
        if len(admin_password) < 8:
            errors.append("Le mot de passe doit contenir au moins 8 caractères")
        
        # Vérifier si l'email existe déjà
        if Client.objects.filter(email=email_entreprise).exists():
            errors.append("Une entreprise avec cet email existe déjà")
        
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'tenants/inscription.html', {
                'form_data': request.POST
            })
        
        try:
            # Créer le tenant
            client, domain, admin_user = TenantProvisioningService.create_tenant(
                nom_entreprise=nom_entreprise,
                email=email_entreprise,
                admin_email=admin_email,
                admin_password=admin_password,
                admin_nom=admin_nom,
                admin_prenoms=admin_prenoms,
                telephone=telephone,
                adresse=adresse,
                ville=ville,
                nif=nif,
                num_cnss=num_cnss,
                plan_abonnement='gratuit',
                base_domain=request.get_host().split(':')[0]  # Récupérer le domaine de base
            )
            
            messages.success(
                request, 
                f"Votre espace {nom_entreprise} a été créé avec succès! "
                f"Vous pouvez maintenant vous connecter à {domain.domain}"
            )
            
            return redirect('tenants:inscription_success', schema_name=client.schema_name)
            
        except IntegrityError as e:
            messages.error(request, f"Erreur lors de la création: {str(e)}")
        except Exception as e:
            messages.error(request, f"Une erreur est survenue: {str(e)}")
    
    return render(request, 'tenants/inscription.html')


def inscription_success(request, schema_name):
    """
    Page de succès après inscription
    """
    try:
        client = Client.objects.get(schema_name=schema_name)
        domain = client.domains.filter(is_primary=True).first()
        
        return render(request, 'tenants/inscription_success.html', {
            'client': client,
            'domain': domain,
        })
    except Client.DoesNotExist:
        messages.error(request, "Entreprise non trouvée")
        return redirect('tenants:inscription')
