class Signals_Query:
    get_signals_query = """
        query signals($input: SignalFilterInput) {
            signal(input: $input) {
                name
                unit
                paramType
                paramId
                messageName
                configurationId
                messageId
                networkName
            }
        }
    """

    get_signals_data_query = """
        query signalData($input: SignalDataFilterInput) {
            signalData(input: $input) {
                vehicleId
                name
                time
                value
                svalue
            }
        }
    """

class Signals_Mutation:
    upsert_signal_data_mutation = """
        mutation UpsertSignalData($input: UpsertSignalDataInput) {
            upsertSignalData(input: $input) {
                configurationId
                messageId
                messageName
                name
                paramType
                unit
            }
        }
    """

    delete_signal_data_mutation = """
        mutation DeleteSignalData($input: DeleteSignalDataInput) {
            deleteSignalData(input: $input) {
               configurations
            }
        }
    """
