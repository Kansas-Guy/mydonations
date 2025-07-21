(function() {
  // 1) Instantiate the add-in client
  const client = new BBSkyAddinClient.AddinClient({
    callbacks: {
      init: async function(args) {
        console.log('Sky Add‑in init args:', args);
        console.log('Context payload:', args.context);

        args.ready({ showUI: true, title: 'Decline Event' });
        // —————————————————————————————
        // 2) SSO: Fetch the user‑identity token for your backend
        const identityToken = await client.getUserIdentityToken();
        const recordId = args.context.recordId;
        // envId lets your backend scope consent to the right BB environment
        const envid = args.envId;

        const SKY_OAUTH_CLIENT_ID   = '3b9c4ffd-ed8c-4682-9e23-43032fc886a5';
        const SKY_OAUTH_REDIRECT_URI = 'https://mydonations-7bb26315ee30.herokuapp.com/skyapi/oauth/callback';
        const SUBSCRIPTION_KEY = '7f87e63978a746bfbec6783f4e46207b';

        let skyApiToken = null;

        const connectBtn = document.getElementById('connect');
        connectBtn.addEventListener('click', () => {
          // — open popup synchronously inside the click handler —
          const authUrl = `/skyapi/authorize?token=${encodeURIComponent(identityToken)}&envid=${encodeURIComponent(envid)}`;
          const popup = window.open(
            authUrl,
            '_blank',
            'toolbar=0,status=0,width=600,height=500'
          );
          if (!popup) {
            console.error('Popup blocked by browser');
            return;
          }
          console.log('popup returned →', popup);

          // — poll until it closes —
          const iv = setInterval(async () => {
            if (popup.closed) {
              clearInterval(iv);
              try {
                const resp = await fetch('/skyapi/token', { credentials: 'include' });
                if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
                const { accessToken } = await resp.json();
                skyApiToken = accessToken;
                loadEvents();
              } catch (err) {
                console.error('Failed to fetch SKY API token:', err);
                document.getElementById('status').textContent = 'Unable to connect to SKY API';
              }
            }
          }, 100);
        });

        // 7) Helper to call the SKY API once we have skyApiToken

        async function skyFetch(path, opts = {}) {
          if (!skyApiToken) {
            throw new Error('Missing SKY API token – call connectToSkyApi() first.');
          }
          const url = `https://api.sky.blackbaud.com${path}`;
          const res = await fetch(url, {
            ...opts,
            credentials: 'include',
            headers: {
              ...opts.headers,
              Authorization: `Bearer ${skyApiToken}`,
              'Bb-Api-Subscription-Key': SUBSCRIPTION_KEY,
              'Content-Type': 'application/json',
            },
          });
          if (!res.ok) {
            const text = await res.text();
            console.error(`❌ skyFetch ${path} →`, res.status, text);
            throw new Error(text);
          }
          return res.json();
        }

        // 8) Pull & render your events dropdown
        async function loadEvents() {
          try {
            const { value: events } = await skyFetch('/event/v1/events');
            const select = document.getElementById('events');
            select.innerHTML = '';
            events.forEach(e => {
              const opt = document.createElement('option');
              opt.value = e.id;
              opt.textContent = `${e.name} (${e.start_date})`;
              select.append(opt);
            });
          } catch {
            document.getElementById('status').textContent =
              'Error loading events';
          }
        }

        // 9) Wire up the Decline button (same as before)
        document
          .getElementById('submit')
          .addEventListener('click', async () => {
            const eventId = document.getElementById('events').value;
            const notAttending = document.getElementById('decline').checked;
            const statusEl = document.getElementById('status');
            if (!notAttending) {
              statusEl.textContent = 'Check “Not attending”';
              return;
            }
            try {
              await skyFetch(
                `/event/v1/events/${eventId}/participants`,
                {
                  method: 'POST',
                  body: JSON.stringify({
                    event_id: eventId,
                    constituent_id: args.context.recordId,
                    invitation_status: 'Declined',
                  }),
                }
              );
              statusEl.textContent = 'Successfully declined!';
            } catch {
              statusEl.textContent = 'Error declining attendance';
            }
          });
      },
    },
  });
})();
