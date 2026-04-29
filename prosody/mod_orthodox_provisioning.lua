-- Orthodox Connect - Developed by dgm (dgm@tuta.com)
-- orthodox-connect/prosody/mod_orthodox_provisioning.lua

local json        = require 'util.json'
local jid         = require 'util.jid'
local usermanager = require 'core.usermanager'

local token_file  = module:get_option_string('orthodox_provisioning_token_file')
local xmpp_domain = module:get_option_string('orthodox_provisioning_domain')
local muc_domain  = module:get_option_string('orthodox_provisioning_muc_domain')

if not token_file or token_file == '' then
	error('missing orthodox_provisioning_token_file')
end

if not xmpp_domain or xmpp_domain == '' then
	error('missing orthodox_provisioning_domain')
end

if not muc_domain or muc_domain == '' then
	error('missing orthodox_provisioning_muc_domain')
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

	if action == 'create_room' then
		return handle_room_request(payload)
	end

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

function handle_room_request(payload)
	local room_node, room_host = jid.split(payload.room_jid or '')

	if not room_node or room_host ~= muc_domain then
		return make_response(400, { error = 'room jid is outside the configured muc domain' })
	end

	local muc_host = prosody.hosts[muc_domain]

	if not muc_host or not muc_host.modules or not muc_host.modules.muc then
		return make_response(500, { error = 'muc service is not available' })
	end

	local muc_module = muc_host.modules.muc
	local room       = muc_module.get_room_from_jid(payload.room_jid)
	local status     = 'updated'

	if not room then
		local error_text
		room, error_text = muc_module.create_room(payload.room_jid)

		if not room then
			return make_response(500, { error = error_text or 'failed to create muc room' })
		end

		status = 'created'
	end

	if type(payload.name) == 'string' then
		room:set_name(payload.name)
	end

	if type(payload.description) == 'string' then
		room:set_description(payload.description)
	end

	room:set_persistent(true)
	room:set_members_only(payload.members_only and true or false)
	room:set_public(payload.public and true or false)
	room:set_hidden(not payload.public)
	room:set_moderated(payload.moderated and true or false)

	if type(payload.members) == 'table' then
		apply_members(room, payload.members)
	end

	room:save(true)

	return make_response(status == 'created' and 201 or 200, { jid = payload.room_jid, status = status })
end

function apply_members(room, members)
	local seen = {}

	for _, member_jid in ipairs(members) do
		local member_node, member_host = jid.split(member_jid)

		if member_node and member_host == xmpp_domain then
			seen[member_jid] = true
			room:set_affiliation(true, member_jid, 'member', 'Portal room access')
		end
	end

	for affiliate_jid, affiliation in pairs(room._affiliations or {}) do
		if affiliation == 'member' and not seen[affiliate_jid] then
			room:set_affiliation(true, affiliate_jid, 'none', 'Portal room access removed')
		end
	end
end

module:depends('http')
module:provides('http', {
	route = {
		['POST /account'] = handle_request;
	};
})
