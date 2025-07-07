{{ fullname | escape | underline}}



Class inheritance-diagram
~~~~~~~~~~~~~~~~~~~~~~~~~

.. inheritance-diagram::
   {{ module }}.{{ name }}
   :include-subclasses:
|

Module Overview
~~~~~~~~~~~~~~~~~~~~~~~

.. currentmodule:: {{ module }}
   

.. autoclass:: {{ objname }}




   {% block methods %}



   {% if methods %}



   .. dropdown:: {{ _('Methods') }}

      .. autosummary::

      {% for item in methods %}
         ~{{ name }}.{{ item }}
      {%- endfor %}


   {% endif %}
   {% endblock %}

   {% block attributes %}
   {% if attributes %}

   .. dropdown:: {{ _('Attributes') }}

      .. autosummary::
      {% for item in attributes %}
         ~{{ name }}.{{ item }}
      {%- endfor %}
   {% endif %}
   {% endblock %}

 
   
   {% for item in methods %}
   .. automethod:: {{ item }}
   {%- endfor %}
   {% for item in attributes %}
   ..  autoattribute:: {{ item }}
   {%- endfor %}


