{{ fullname | escape | underline}}

.. automodule:: {{ fullname }}

   {% block attributes %}
   {%- if attributes %}
   .. dropdown:: {{ _('Module Attributes') }}

      .. autosummary::
      {% for item in attributes if not item.startswith('_') %}
         {{ item }}
      {%- endfor %}
   {% endif %}
   {%- endblock %}

   {%- block functions %}
   {%- if functions %}
   .. dropdown:: {{ _('Functions') }}

      .. autosummary::
      {% for item in functions if not item.startswith('_') %}
         {{ item }}
      {%- endfor %}
   {% endif %}
   {%- endblock %}

   {%- block classes %}
   {%- if classes %}
   .. rubric:: Classes

   .. autosummary::
   {% for item in classes if not item.startswith('_') %}
      {{ item }}
   {%- endfor %}
   {% endif %}
   {%- endblock %}

   {%- block exceptions %}
   {%- if exceptions %}
   .. dropdown:: {{ _('Exceptions') }}

      .. autosummary::
      {% for item in exceptions if not item.startswith('_') %}
         {{ item }}
      {%- endfor %}
   {% endif %}
   {%- endblock %}



{%- block modules %}
{%- if modules %}
.. dropdown:: Modules

   .. autosummary::
      :toctree:
      :recursive:
   {% for item in modules if not item.startswith('_') %}
      {{ item }}
   {%- endfor %}
{% endif %}
{%- endblock %}


