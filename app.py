import streamlit as st
import json
import os

st.set_page_config(page_title="Kinaxis Maestro Documentation", layout="wide")

DATA_FILE = "data.json"


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "applications": [],
        "relations": [],
        "table_relations": []
    }


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


data = load_data()

st.title("Kinaxis Maestro Documentation Tool")
st.write("Navigation entre Applications, Algorithms et Tables")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Applications")

    if not data["applications"]:
        st.warning("Aucune application disponible.")
    else:
        selected_app = st.selectbox(
            "Choisir une application",
            data["applications"]
        )

        st.markdown("### Algorithms liés")

        linked_algorithms = [
            rel for rel in data["relations"]
            if rel["application"] == selected_app
        ]

        if linked_algorithms:
            for rel in linked_algorithms:
                st.markdown(f"**{rel['algorithm']}**")
                st.write(f"Description de la relation : {rel['relation_description']}")

                linked_tables = [
                    tbl for tbl in data["table_relations"]
                    if tbl["algorithm"] == rel["algorithm"]
                ]

                if linked_tables:
                    st.write("Tables liées :")
                    for tbl in linked_tables:
                        st.write(f"- {tbl['table_name']} | Type : {tbl['relation_type']}")
                        if tbl["relation_description"]:
                            st.write(f"  Description : {tbl['relation_description']}")
                else:
                    st.write("Aucune table liée pour le moment.")

                st.write("---")
        else:
            st.info("Aucun algorithm lié à cette application pour le moment.")

with col2:
    st.subheader("Admin")

    # Liste des algorithmes existants
    all_algorithms = sorted(list({rel["algorithm"] for rel in data["relations"]}))

    # Ajouter un algorithm
    with st.expander("+ Ajouter un algorithm"):
        with st.form("add_algorithm_form"):
            algorithm_name = st.text_input("Nom de l'algorithm")
            application_name = st.selectbox("Choisir l'application liée", data["applications"])
            relation_description = st.text_area("Description de la relation App → Algorithm")

            submitted = st.form_submit_button("Enregistrer l'algorithm")

            if submitted:
                if algorithm_name.strip() == "":
                    st.error("Le nom de l'algorithm est obligatoire.")
                else:
                    new_relation = {
                        "application": application_name,
                        "algorithm": algorithm_name.strip(),
                        "relation_description": relation_description.strip()
                    }

                    data["relations"].append(new_relation)
                    save_data(data)

                    st.success("Algorithm ajouté avec succès.")
                    st.rerun()

    # Ajouter une table
    with st.expander("+ Ajouter une table"):
        if not all_algorithms:
            st.warning("Ajoute d'abord au moins un algorithm.")
        else:
            with st.form("add_table_form"):
                table_name = st.text_input("Nom de la table")
                algorithm_name = st.selectbox("Choisir l'algorithm lié", all_algorithms)
                relation_type = st.selectbox(
                    "Type de relation",
                    ["Input", "Output", "Constraint", "Parameter", "Reference", "Other"]
                )
                relation_description = st.text_area("Description de la relation Algorithm → Table")

                submitted_table = st.form_submit_button("Enregistrer la table")

                if submitted_table:
                    if table_name.strip() == "":
                        st.error("Le nom de la table est obligatoire.")
                    else:
                        new_table_relation = {
                            "algorithm": algorithm_name,
                            "table_name": table_name.strip(),
                            "relation_type": relation_type,
                            "relation_description": relation_description.strip()
                        }

                        data["table_relations"].append(new_table_relation)
                        save_data(data)

                        st.success("Table ajoutée avec succès.")
                        st.rerun()

    # Modifier ou supprimer un algorithm
    with st.expander("Modifier / Supprimer un algorithm"):
        if not data["relations"]:
            st.info("Aucun algorithm à modifier.")
        else:
            algo_options = [
                f"{idx} - {rel['application']} -> {rel['algorithm']}"
                for idx, rel in enumerate(data["relations"])
            ]

            selected_algo_option = st.selectbox(
                "Choisir un algorithm",
                algo_options,
                key="select_algo_to_edit"
            )

            selected_algo_index = int(selected_algo_option.split(" - ")[0])
            selected_algo = data["relations"][selected_algo_index]

            new_algorithm_name = st.text_input(
                "Nom de l'algorithm",
                value=selected_algo["algorithm"],
                key="edit_algo_name"
            )

            new_application_name = st.selectbox(
                "Application liée",
                data["applications"],
                index=data["applications"].index(selected_algo["application"]),
                key="edit_algo_app"
            )

            new_relation_description = st.text_area(
                "Description de la relation",
                value=selected_algo["relation_description"],
                key="edit_algo_desc"
            )

            col_edit_algo, col_delete_algo = st.columns(2)

            with col_edit_algo:
                if st.button("Enregistrer les modifications de l'algorithm"):
                    old_algo_name = data["relations"][selected_algo_index]["algorithm"]

                    data["relations"][selected_algo_index]["algorithm"] = new_algorithm_name.strip()
                    data["relations"][selected_algo_index]["application"] = new_application_name
                    data["relations"][selected_algo_index]["relation_description"] = new_relation_description.strip()

                    for tbl in data["table_relations"]:
                        if tbl["algorithm"] == old_algo_name:
                            tbl["algorithm"] = new_algorithm_name.strip()

                    save_data(data)
                    st.success("Algorithm modifié avec succès.")
                    st.rerun()

            with col_delete_algo:
                if st.button("Supprimer totalement cet algorithm"):
                    algo_to_delete = data["relations"][selected_algo_index]["algorithm"]

                    # Supprimer l'algorithm
                    del data["relations"][selected_algo_index]

                    # Supprimer toutes les tables liées
                    data["table_relations"] = [
                        tbl for tbl in data["table_relations"]
                        if tbl["algorithm"] != algo_to_delete
                    ]

                    save_data(data)
                    st.success("Algorithm et tables liées supprimés avec succès.")
                    st.rerun()

    # Modifier ou supprimer une table
    with st.expander("Modifier / Supprimer une table"):
        if not data["table_relations"]:
            st.info("Aucune table à modifier.")
        else:
            table_options = [
                f"{idx} - {tbl['algorithm']} -> {tbl['table_name']}"
                for idx, tbl in enumerate(data["table_relations"])
            ]

            selected_table_option = st.selectbox(
                "Choisir une table",
                table_options,
                key="select_table_to_edit"
            )

            selected_table_index = int(selected_table_option.split(" - ")[0])
            selected_table = data["table_relations"][selected_table_index]

            updated_algorithms = sorted(list({rel["algorithm"] for rel in data["relations"]}))

            new_table_name = st.text_input(
                "Nom de la table",
                value=selected_table["table_name"],
                key="edit_table_name"
            )

            new_algorithm_name_for_table = st.selectbox(
                "Algorithm lié",
                updated_algorithms,
                index=updated_algorithms.index(selected_table["algorithm"]),
                key="edit_table_algo"
            )

            relation_type_options = ["Input", "Output", "Constraint", "Parameter", "Reference", "Other"]
            new_relation_type = st.selectbox(
                "Type de relation",
                relation_type_options,
                index=relation_type_options.index(selected_table["relation_type"]),
                key="edit_table_type"
            )

            new_table_relation_description = st.text_area(
                "Description de la relation",
                value=selected_table["relation_description"],
                key="edit_table_desc"
            )

            col_edit_table, col_delete_table = st.columns(2)

            with col_edit_table:
                if st.button("Enregistrer les modifications de la table"):
                    data["table_relations"][selected_table_index]["table_name"] = new_table_name.strip()
                    data["table_relations"][selected_table_index]["algorithm"] = new_algorithm_name_for_table
                    data["table_relations"][selected_table_index]["relation_type"] = new_relation_type
                    data["table_relations"][selected_table_index]["relation_description"] = new_table_relation_description.strip()

                    save_data(data)
                    st.success("Table modifiée avec succès.")
                    st.rerun()

            with col_delete_table:
                if st.button("Supprimer totalement cette table"):
                    del data["table_relations"][selected_table_index]

                    save_data(data)
                    st.success("Table supprimée avec succès.")
                    st.rerun()