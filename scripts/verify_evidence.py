from ai_data_incident_investigator.data.object_storage import (
    download_bytes,
    list_objects,
)


INCIDENT_ID = "90313020-a51b-40c5-9576-ed0ba1d91a18"


def main() -> None:
    prefix = f"{INCIDENT_ID}/evidence/"

    objects = list_objects(prefix)

    print("Objects:")
    for object_name in objects:
        print(f"  {object_name}")

    object_name = (
        f"{INCIDENT_ID}/evidence/"
        "pipeline_execution_report.txt"
    )

    content = download_bytes(object_name)

    print(f"\nDownloaded bytes: {len(content)}")

    print("\nContent:")
    print(content.decode("utf-8"))


if __name__ == "__main__":
    main()