.. PR Pilot documentation master file, created by
   sphinx-quickstart on Tue Mar  5 20:35:25 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

PR Pilot Documentation
======================

Save time and stay in the flow by delegating routine work to AI with confidence and predictability. PR Pilot assist you in your daily workflow and works with the dev tools you trust and love - exactly when and where you want it.


Quick Start
-----------

First, `add PR Pilot to your GitHub repository <https://github.com/apps/pr-pilot-ai/installations/new>`_.

Then, install the CLI:

.. code-block:: bash

   ➜ brew tap pr-pilot-ai/homebrew-tap
   ➜ brew install pr-pilot-cli

Get your API Key from the `dashboard <https://app.pr-pilot.ai/dashboard/api-keys/>`_ and you're ready to go!


.. code-block:: bash

   pilot edit README.md "Add emojis to all headers"

If you like, grab some commands from our core repository:

.. code-block:: bash

   ➜ pilot grab commands pr-pilot-ai/core

   Found the following commands in pr-pilot-ai/core:

     Name            Description
     haiku           Writes a Haiku about your project
     test-analysis   Run the tests, analyze the output and provide suggestions
     daily-report    Assemble a comprehensive daily report and send it to Slack
     pr-description  Generate PR Title and Description

   [?] Which commands would you like to add?:
      [ ] haiku
      [X] test-analysis
      [ ] daily-report
    > [X] pr-description


   You can now use the following commands:

     pilot run test-analysis   Run the tests, analyze the output and provide suggestions
     pilot run pr-description  Generate PR Title and Description

To learn more, head over to our `User Guide <user_guide.html>`_ or get inspiration
from our `Demo Repository <https://github.com/PR-Pilot-AI/demo>`_.

.. toctree::
   :maxdepth: 0
   :hidden:

   user_guide
   capabilities
   vision
   roadmap
   pricing
   privacy_notice
   support
   team
   faq
