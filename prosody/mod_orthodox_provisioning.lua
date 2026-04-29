-- Orthodox Connect - Developed by dgm (dgm@tuta.com)
-- orthodox-connect/prosody/mod_orthodox_provisioning.lua

local json        = require 'util.json'
local jid         = require 'util.jid'
local usermanager = require 'core.usermanager'

local token_file  = module:get_option_string('orthodox_provisioning_token_file')
local xmpp_domain = module:get_option_string('orthodox_provisioning_domain')

if not token_file or token_file == '' then
	error('missing orthodox_provisioning_token_file')
end

if not xmpp_domain or xmpp_domain == '' then
	error('missing orthodox_provisioning_domain')
end

local function read_token()
	local handle = io.open(token_file, 'r')

	if not handle then
		return nil
	end

	local token = handle:read('*a')
	handle:close()

	return token and token:gsub('^%s+', ''):gsub('%s+$', '')
end

local provisioning_token = read_token()

if not provisioning_token or provisioning_token == '' then
	error('missing provisioning token')
end

local function make_response(status_code, payload)
	return {
		status_code = status_code;
		headers     = { ['Content-Type'] = 'application/json' };
		body        = json.encode(payload);
	}
end

local function is_authorized(request)
	local authorization = request.headers.authorization or ''

	return authorization == 'Bearer ' .. provisioning_token
end

local function handle_request(event)
	local request = event.request

	if not is_authorized(request) then
		return make_response(401, { error = 'unauthorized' })
	end

	local ok, payload = pcall(json.decode, request.body or '')

	if not ok or type(payload) ~= 'table' then
		return make_response(400, { error = 'invalid json body' })
	end

	local action   = payload.action
	local password = payload.password
	local node, host = jid.split(payload.jid or '')

	if not node or host ~= xmpp_domain then
		return make_response(400, { error = 'jid is outside the configured xmpp domain' })
	end

	if action == 'create' then
		if type(password) ~= 'string' or password == '' then
			return make_response(400, { error = 'password is required' })
		end

		if usermanager.user_exists(node, host) then
			local changed, error_text = usermanager.set_password(node, password, host)

			if not changed then
				return make_response(500, { error = error_text or 'failed to update xmpp account' })
			end

			return make_response(200, { jid = payload.jid, status = 'updated' })
		end

		local created, error_text = usermanager.create_user(node, password, host)

		if not created then
			return make_response(500, { error = error_text or 'failed to create xmpp account' })
		end

		return make_response(201, { jid = payload.jid, status = 'created' })
	end

	if action == 'disable' then
		if not usermanager.user_exists(node, host) then
			return make_response(200, { jid = payload.jid, status = 'missing' })
		end

		local deleted, error_text = usermanager.delete_user(node, host)

		if not deleted then
			return make_response(500, { error = error_text or 'failed to disable xmpp account' })
		end

		return make_response(200, { jid = payload.jid, status = 'disabled' })
	end

	return make_response(400, { error = 'unsupported action' })
end

module:depends('http')
module:provides('http', {
	route = {
		['POST /account'] = handle_request;
	};
})
