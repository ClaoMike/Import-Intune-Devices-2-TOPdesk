def generate_new_user_asset_data_as_json(asset_name, template_id, userId):
    print(f"Updating TOPdesk asset with user: {userId}")

    json = {
        "name": f"{asset_name}",  # asset id
        "type_id": template_id,  # asset template
        "user-id": userId,
    }

    return json