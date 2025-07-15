(function() {
  // 1) Instantiate the add-in client
  const client = new BBSkyAddinClient.AddinClient({
    callbacks: {
      init: async function(args) {
        console.log('Sky Add‑in init args:', args);
        console.log('Context payload:', args.context);

        // —————————————————————————————
        // 2) SSO: Fetch the user‑identity token for your backend
        const userIdentityToken = await client.getUserIdentityToken();
        // envId lets your backend scope consent to the right BB environment
        const envid = args.envId;

        // 3) Tell NXT you’re ready
        args.ready({ showUI: true, title: 'Decline Event' });

        // 4) State for your SKY API token (once we fetch it)
        let skyApiToken = null;

        // 5) Wire up “Connect to Sky API” button
        const connectBtn = document.getElementById('connect');
        connectBtn.addEventListener('click', connectToSkyApi);

        // 6) Popup + poll until closed, then grab the token from your backend:
         function connectToSkyApi() {
           // 1) CSRF/state
           const state = Math.random().toString(36).slice(2);
            localStorage.setItem('bb_oauth_state', state);

            // 2) full BB OAuth URL
            const url =
             'https://oauth2.sky.blackbaud.com/authorization?'
               + `response_type=code`
               + `&client_id=${encodeURIComponent(YOUR_CLIENT_ID)}`
               + `&redirect_uri=${encodeURIComponent(YOUR_REDIRECT_URI)}`
               + `&state=${encodeURIComponent(state)}`
               + `&environment_id=${encodeURIComponent(envid)}`;

          const width = 625, height = 500;
          const top = window.screenY + (window.outerHeight - height) / 2;
          const left = window.screenX + (window.outerWidth - width) / 2;
          const opts = `toolbar=0,status=0,width=${width},height=${height},top=${top},left=${left}`;

          const child = window.open(url, '_blank', opts);
          const timer = setInterval(async () => {
            if (child.closed) {
              clearInterval(timer);

              try {
                // backend should read the code & state, swap it for an access token, then return it here
                const resp = await fetch(
                  `/skyapi/token?token=${encodeURIComponent(userIdentityToken)}`,
                  { credentials: 'include' }
                );
                const { accessToken } = await resp.json();
                skyApiToken = accessToken;
                // now that we have a SKY API token, load events
                loadEvents();
              } catch (err) {
                console.error('❌ could not fetch SKY API token', err);
                document.getElementById('status').textContent =
                  'Unable to connect to SKY API';
              }
            }
          }, 100);
        }

        // 7) Helper to call the SKY API once we have skyApiToken
        const SUBSCRIPTION_KEY = '7f87e63978a746bfbec6783f4e46207b';
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

        // 10) Optionally auto‑connect if your backend has already set a cookie/session:
        // connectToSkyApi();
      },
    },
  });
})();
