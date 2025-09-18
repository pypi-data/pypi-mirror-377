from django.shortcuts import redirect,get_object_or_404
from home.models import Pagina, Site
from django.views.generic import View

class BasePageView(View):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['site'] = self.get_site()

        pagina = self.get_pagina()

        menu = pagina.menu_set.first()
        if menu:
            items_menu = menu.itemmenu_set.filter(
                item_menu_pai__isnull=True,
            ).order_by("order")
            menu_codigo = f"menus/{menu.codigo}.html"
        else:
            items_menu = None
            menu_codigo = None

        context['items_menu'] = items_menu
        context['menu_codigo'] = menu_codigo

        return context

    def get_template_names(self):
        pagina = self.get_pagina()
        return pagina.template
    
    def get_site(self):
        return Site.objects.all().first()

    def dispatch(self, request, *args, **kwargs):
        site = self.get_site()
        em_manutencao = site.ativar_manutencao
        em_coming_soon = site.ativar_coming_soon

        if em_manutencao and not request.user.is_authenticated:
            return redirect("manutencao")

        if em_coming_soon and not request.user.is_authenticated:
            return redirect("coming_soon")

        return super().dispatch(request, *args, **kwargs)
    
    def get_pagina(self):
        slug = self.kwargs.get('slug', None)  
        pagina = get_object_or_404(Pagina, slug=slug)
        return pagina
