{{ fullname | escape | underline}}

.. automodule:: {{ fullname }}

   {% block attributes %}
   {%- if attributes %}
   .. dropdown:: {{ _('Module Attributes') }}

      .. autosummary::
      {% for item in attributes %}
         {{ item }}
      {%- endfor %}
   {% endif %}
   {%- endblock %}

   {%- block functions %}
   {%- if functions %}
   .. dropdown:: {{ _('Functions') }}

      .. autosummary::
      {% for item in functions %}
         {{ item }}
      {%- endfor %}
   {% endif %}
   {%- endblock %}

   {%- block classes %}
   {%- if classes %}
   .. rubric:: Classes

   .. autosummary::
      :toctree:
   {% for item in classes %}
      {{ item }}
   {%- endfor %}
   {% else %}
   {% for item in classes %}
      {{ item }}
   {%- endfor %}
   {% endif %}
   {%- endblock %}

   {%- block exceptions %}
   {%- if exceptions %}
   .. dropdown:: {{ _('Exceptions') }}

      .. autosummary::
      {% for item in exceptions %}
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
   {% for item in modules %}
      {{ item }}
   {%- endfor %}
{% endif %}
{%- endblock %}


