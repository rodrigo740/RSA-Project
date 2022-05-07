/*
 * Generated by asn1c-0.9.29 (http://lionet.info/asn1c)
 * From ASN.1 module "ITS-Container"
 * 	found in "asn1/TS102894-2v131-CDD.asn"
 * 	`asn1c -fcompound-names -fincludes-quoted -no-gen-example -R`
 */

#ifndef	_CauseCodeType_H_
#define	_CauseCodeType_H_


#include "asn_application.h"

/* Including external dependencies */
#include "NativeInteger.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Dependencies */
typedef enum CauseCodeType {
	CauseCodeType_reserved	= 0,
	CauseCodeType_trafficCondition	= 1,
	CauseCodeType_accident	= 2,
	CauseCodeType_roadworks	= 3,
	CauseCodeType_impassability	= 5,
	CauseCodeType_adverseWeatherCondition_Adhesion	= 6,
	CauseCodeType_aquaplannning	= 7,
	CauseCodeType_hazardousLocation_SurfaceCondition	= 9,
	CauseCodeType_hazardousLocation_ObstacleOnTheRoad	= 10,
	CauseCodeType_hazardousLocation_AnimalOnTheRoad	= 11,
	CauseCodeType_humanPresenceOnTheRoad	= 12,
	CauseCodeType_wrongWayDriving	= 14,
	CauseCodeType_rescueAndRecoveryWorkInProgress	= 15,
	CauseCodeType_adverseWeatherCondition_ExtremeWeatherCondition	= 17,
	CauseCodeType_adverseWeatherCondition_Visibility	= 18,
	CauseCodeType_adverseWeatherCondition_Precipitation	= 19,
	CauseCodeType_slowVehicle	= 26,
	CauseCodeType_dangerousEndOfQueue	= 27,
	CauseCodeType_vehicleBreakdown	= 91,
	CauseCodeType_postCrash	= 92,
	CauseCodeType_humanProblem	= 93,
	CauseCodeType_stationaryVehicle	= 94,
	CauseCodeType_emergencyVehicleApproaching	= 95,
	CauseCodeType_hazardousLocation_DangerousCurve	= 96,
	CauseCodeType_collisionRisk	= 97,
	CauseCodeType_signalViolation	= 98,
	CauseCodeType_dangerousSituation	= 99
} e_CauseCodeType;

/* CauseCodeType */
typedef long	 CauseCodeType_t;

/* Implementation */
extern asn_per_constraints_t asn_PER_type_CauseCodeType_constr_1;
extern asn_TYPE_descriptor_t asn_DEF_CauseCodeType;
asn_struct_free_f CauseCodeType_free;
asn_struct_print_f CauseCodeType_print;
asn_constr_check_f CauseCodeType_constraint;
ber_type_decoder_f CauseCodeType_decode_ber;
der_type_encoder_f CauseCodeType_encode_der;
xer_type_decoder_f CauseCodeType_decode_xer;
xer_type_encoder_f CauseCodeType_encode_xer;
oer_type_decoder_f CauseCodeType_decode_oer;
oer_type_encoder_f CauseCodeType_encode_oer;
per_type_decoder_f CauseCodeType_decode_uper;
per_type_encoder_f CauseCodeType_encode_uper;
per_type_decoder_f CauseCodeType_decode_aper;
per_type_encoder_f CauseCodeType_encode_aper;

#ifdef __cplusplus
}
#endif

#endif	/* _CauseCodeType_H_ */
#include "asn_internal.h"
