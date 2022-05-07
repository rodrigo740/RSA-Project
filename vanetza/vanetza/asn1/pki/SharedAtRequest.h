/*
 * Generated by asn1c-0.9.29 (http://lionet.info/asn1c)
 * From ASN.1 module "EtsiTs102941TypesAuthorization"
 * 	found in "asn1/TS102941v131-TypesAuthorization.asn"
 * 	`asn1c -fcompound-names -fincludes-quoted -no-gen-example -R`
 */

#ifndef	_SharedAtRequest_H_
#define	_SharedAtRequest_H_


#include "asn_application.h"

/* Including external dependencies */
#include "HashedId8.h"
#include "OCTET_STRING.h"
#include "CertificateFormat.h"
#include "CertificateSubjectAttributes.h"
#include "constr_SEQUENCE.h"

#ifdef __cplusplus
extern "C" {
#endif

/* SharedAtRequest */
typedef struct SharedAtRequest {
	HashedId8_t	 eaId;
	OCTET_STRING_t	 keyTag;
	CertificateFormat_t	 certificateFormat;
	CertificateSubjectAttributes_t	 requestedSubjectAttributes;
	/*
	 * This type is extensible,
	 * possible extensions are below.
	 */
	
	/* Context for parsing across buffer boundaries */
	asn_struct_ctx_t _asn_ctx;
} SharedAtRequest_t;

/* Implementation */
extern asn_TYPE_descriptor_t asn_DEF_SharedAtRequest;
extern asn_SEQUENCE_specifics_t asn_SPC_SharedAtRequest_specs_1;
extern asn_TYPE_member_t asn_MBR_SharedAtRequest_1[4];

#ifdef __cplusplus
}
#endif

#endif	/* _SharedAtRequest_H_ */
#include "asn_internal.h"
